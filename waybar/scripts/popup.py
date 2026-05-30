
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import subprocess
import urllib.request
import tempfile
import sys
import threading

def playerctl(*args):
    try:
        return subprocess.check_output(
            ["playerctl", "-p", "spotify", *args],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except subprocess.CalledProcessError:
        return ""

def get_art_url():
    return playerctl("metadata", "mpris:artUrl")

def fetch_art(url):
    try:
        if url.startswith("file://"):
            return url[7:]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        urllib.request.urlretrieve(url, tmp.name)
        return tmp.name
    except Exception:
        return None

def fmt_duration(microseconds):
    try:
        secs = int(microseconds) // 1_000_000
        return f"{secs // 60}:{secs % 60:02d}"
    except Exception:
        return "0:00"


class MusicPopup(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("music-popup")  # used by Hyprland window rules
        self.set_name("music-popup")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_default_size(340, 1)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        # close on Escape or click-outside
        self.connect("key-press-event", self._on_key)
        self.add_events(Gdk.EventMask.FOCUS_CHANGE_MASK)
        self.connect("focus-out-event", self._on_focus_out)
        self._allow_focus_out = False

        css = b"""
        #music-popup {
            background-color: #0d0d0d;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
        }
        #track-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 22px;
            color: #f0f0f0;
            letter-spacing: 1px;
        }
        #track-artist {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            color: #c85a0a;
            letter-spacing: 2px;
        }
        #time-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 10px;
            color: #444444;
        }
        .ctrl-btn {
            background: none;
            border: none;
            color: #555555;
            padding: 4px 10px;
            font-size: 18px;
            border-radius: 6px;
        }
        .ctrl-btn:hover {
            background-color: #1a1a1a;
            color: #e8e8e8;
        }
        .play-btn {
            background-color: #c85a0a;
            border: none;
            color: #ffffff;
            padding: 6px 16px;
            border-radius: 22px;
            font-size: 18px;
        }
        .play-btn:hover {
            background-color: #e8742a;
        }
        #progress-bar trough {
            background-color: #222222;
            border-radius: 2px;
            min-height: 3px;
        }
        #progress-bar progress {
            background-color: #c85a0a;
            border-radius: 2px;
        }
        #bottom-bar {
            background-color: #111111;
            border-radius: 0 0 12px 12px;
            border-top: 1px solid #1e1e1e;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(outer)

        # album art
        self.art_box = Gtk.Box()
        self.art_box.set_size_request(340, 200)
        self.art_image = Gtk.Image()
        self.art_box.pack_start(self.art_image, True, True, 0)
        outer.pack_start(self.art_box, False, False, 0)

        # info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_margin_start(18)
        info_box.set_margin_end(18)
        info_box.set_margin_top(12)
        info_box.set_margin_bottom(4)
        outer.pack_start(info_box, False, False, 0)

        self.title_label = Gtk.Label(label="")
        self.title_label.set_name("track-title")
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.set_ellipsize(3)
        info_box.pack_start(self.title_label, False, False, 0)

        self.artist_label = Gtk.Label(label="")
        self.artist_label.set_name("track-artist")
        self.artist_label.set_halign(Gtk.Align.START)
        info_box.pack_start(self.artist_label, False, False, 0)

        # progress
        prog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        prog_box.set_margin_start(18)
        prog_box.set_margin_end(18)
        prog_box.set_margin_top(8)
        outer.pack_start(prog_box, False, False, 0)

        self.progress = Gtk.ProgressBar()
        self.progress.set_name("progress-bar")
        self.progress.set_fraction(0)
        prog_box.pack_start(self.progress, False, False, 0)

        times_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.time_current = Gtk.Label(label="0:00")
        self.time_current.set_name("time-label")
        self.time_total = Gtk.Label(label="0:00")
        self.time_total.set_name("time-label")
        times_box.pack_start(self.time_current, False, False, 0)
        times_box.pack_end(self.time_total, False, False, 0)
        prog_box.pack_start(times_box, False, False, 0)

        # controls
        ctrl_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        ctrl_box.set_halign(Gtk.Align.CENTER)
        ctrl_box.set_margin_top(8)
        ctrl_box.set_margin_bottom(14)
        outer.pack_start(ctrl_box, False, False, 0)

        prev_btn = Gtk.Button(label="⏮")
        prev_btn.get_style_context().add_class("ctrl-btn")
        prev_btn.connect("clicked", lambda _: self.control("previous"))
        ctrl_box.pack_start(prev_btn, False, False, 0)

        self.play_btn = Gtk.Button(label="▶")
        self.play_btn.get_style_context().add_class("play-btn")
        self.play_btn.connect("clicked", lambda _: self.control("play-pause"))
        ctrl_box.pack_start(self.play_btn, False, False, 0)

        next_btn = Gtk.Button(label="⏭")
        next_btn.get_style_context().add_class("ctrl-btn")
        next_btn.connect("clicked", lambda _: self.control("next"))
        ctrl_box.pack_start(next_btn, False, False, 0)

        # volume
        bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bottom.set_margin_start(18)
        bottom.set_margin_end(18)

        vol_lbl = Gtk.Label(label="🔊")
        vol_lbl.set_name("time-label")
        bottom.pack_start(vol_lbl, False, False, 0)

        self.vol_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.vol_slider.set_draw_value(False)
        self.vol_slider.set_value(75)
        self.vol_slider.connect("value-changed", self.on_volume_changed)
        bottom.pack_start(self.vol_slider, True, True, 0)

        outer_bottom = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        outer_bottom.set_name("bottom-bar")
        outer_bottom.pack_start(bottom, False, False, 10)
        outer.pack_start(outer_bottom, False, False, 0)

        self.refresh()
        GLib.timeout_add(1000, self.refresh)

    def _on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

    def _on_focus_out(self, widget, event):
        if self._allow_focus_out:
            self.destroy()

    def control(self, cmd):
        playerctl(cmd)
        GLib.timeout_add(200, self.refresh)

    def on_volume_changed(self, slider):
        vol = int(slider.get_value())
        subprocess.Popen(
            ["playerctl", "-p", "spotify", "volume", str(vol / 100)],
            stderr=subprocess.DEVNULL
        )

    def refresh(self):
        title  = playerctl("metadata", "xesam:title")  or "Nothing playing"
        artist = playerctl("metadata", "xesam:artist") or ""
        status = playerctl("status")

        self.title_label.set_text(title)
        artist_text = artist.upper()
        year = playerctl("metadata", "xesam:contentCreated") or ""
        if year:
            artist_text += f" · {year[:4]}"
        self.artist_label.set_text(artist_text)
        self.play_btn.set_label("⏸" if status == "Playing" else "▶")

        pos = playerctl("position")
        length = playerctl("metadata", "mpris:length")
        if pos and length:
            try:
                frac = float(pos) / (int(length) / 1_000_000)
                self.progress.set_fraction(min(1.0, frac))
                self.time_current.set_text(f"{int(float(pos))//60}:{int(float(pos))%60:02d}")
                self.time_total.set_text(fmt_duration(length))
            except Exception:
                pass

        art_url = get_art_url()
        if art_url and art_url != getattr(self, "_last_art_url", None):
            self._last_art_url = art_url
            threading.Thread(target=self._load_art, args=(art_url,), daemon=True).start()

        return True

    def _load_art(self, url):
        path = fetch_art(url)
        if path:
            GLib.idle_add(self._apply_art, path)

    def _apply_art(self, path):
        try:
            pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 340, 200, False)
            self.art_image.set_from_pixbuf(pb)
        except Exception:
            pass

    def position_near_waybar(self):
        self.show_all()
        self.get_window().set_override_redirect(False)

        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geo = monitor.get_geometry()

        bar_height = 50  # adjust to your waybar height + margin-top
        x = geo.x + 10
        y = geo.y + bar_height

        self.move(x, y)
        self.present()
        # allow focus-out to close only after window is settled
        GLib.timeout_add(300, self._enable_focus_out)

    def _enable_focus_out(self):
        self._allow_focus_out = True
        return False


def main():
    if not playerctl("status"):
        print("Spotify not running.", file=sys.stderr)
        sys.exit(1)

    win = MusicPopup()
    win.connect("destroy", Gtk.main_quit)
    win.position_near_waybar()
    Gtk.main()

if __name__ == "__main__":
    main()
EOF
