import sys
import os
import shutil
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw, GLib, Gdk

CSS = """
window { background-color: #0a0a0a; }
label { color: #00ff41; font-family: 'Courier New', monospace; }
.title-label { font-size: 24px; font-weight: bold; color: #ffb000; }
.status-label { font-size: 14px; color: #888; }
button.suggested-action { 
    background: rgba(0, 255, 65, 0.1); 
    border: 1px solid #00ff41; 
    color: #00ff41; 
    padding: 10px;
}
button.suggested-action:hover { background: #00ff41; color: #000; }
separator { background-color: #333; margin: 10px 0; }
"""

class TuxCleanerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.kiber.tuxcleaner',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        display = Gdk.Display.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.win = Adw.ApplicationWindow(application=self)
        self.win.set_title("TuxCleaner Terminal")
        self.win.set_default_size(450, 450)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        
        # ИСПРАВЛЕННЫЕ ОТСТУПЫ (совместимо со всеми версиями 2026 года)
        box.set_margin_top(40)
        box.set_margin_bottom(40)
        box.set_margin_start(40)
        box.set_margin_end(40)
        
        self.win.set_content(box)

        # Заголовок
        title = Gtk.Label(label="> TUX_CLEANER_INIT")
        title.add_css_class("title-label")
        box.append(title)

        box.append(Gtk.Separator())

        self.status_label = Gtk.Label(label="Готов к сканированию системы...")
        self.status_label.add_css_class("status-label")
        box.append(self.status_label)

        # Информация о мусоре
        self.info_label = Gtk.Label(label="Размер мусора: 0 MB")
        self.info_label.set_margin_top(10)
        self.info_label.set_margin_bottom(10)
        box.append(self.info_label)

        # Кнопки
        self.btn_scan = Gtk.Button(label="[ СКАНЕР ]")
        self.btn_scan.connect("clicked", self.on_scan_clicked)
        self.btn_scan.add_css_class("suggested-action")
        box.append(self.btn_scan)

        self.btn_clean = Gtk.Button(label="[ ОЧИСТКА ]")
        self.btn_clean.connect("clicked", self.on_clean_clicked)
        self.btn_clean.set_sensitive(False)
        box.append(self.btn_clean)

        self.win.present()

    def get_cache_size(self):
        cache_path = os.path.expanduser('~/.cache')
        total_size = 0
        if os.path.exists(cache_path):
            for dirpath, dirnames, filenames in os.walk(cache_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        try:
                            total_size += os.path.getsize(fp)
                        except OSError:
                            continue
        return total_size

    def on_scan_clicked(self, button):
        self.status_label.set_label("Анализ директорий...")
        # Используем фоновый процесс, чтобы интерфейс не завис
        GLib.idle_add(self.perform_scan)

    def perform_scan(self):
        size = self.get_cache_size()
        size_mb = size / (1024 * 1024)
        self.info_label.set_label(f"Обнаружено мусора: {size_mb:.2f} MB")
        self.status_label.set_label("Сканирование завершено.")
        if size > 0:
            self.btn_clean.set_sensitive(True)
        return False

    def on_clean_clicked(self, button):
        self.status_label.set_label("Удаление временных файлов...")
        cache_path = os.path.expanduser('~/.cache')
        try:
            for filename in os.listdir(cache_path):
                file_path = os.path.join(cache_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception:
                    continue # Пропускаем файлы, которые заняты системой
            self.info_label.set_label("Освобождено: 0 MB")
            self.status_label.set_label("Система очищена!")
            self.btn_clean.set_sensitive(False)
        except Exception as e:
            self.status_label.set_label(f"Ошибка доступа: {str(e)}")

if __name__ == "__main__":
    app = TuxCleanerApp()
    app.run(sys.argv)
