#!/usr/bin/env python3
"""GTK4 GUI for generating tracksheet Excel files from job order CSV reports."""

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from datetime import datetime
from pathlib import Path

from gi.repository import Adw, Gio, GLib, Gtk

from gen_tracksheet import build_tracksheet


class TracksheetApp(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id="com.tracksheet.Generator", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.csv_paths: list[Path] = []
        self.window = None

    def do_activate(self) -> None:
        if self.window:
            self.window.present()
            return

        self.window = Adw.ApplicationWindow(application=self)
        self.window.set_title("Tracksheet Generator")
        self.window.set_default_size(620, 480)

        # ── Toast overlay (outermost) ────────────────────────────────────
        self.toast_overlay = Adw.ToastOverlay()

        # ── Main box ─────────────────────────────────────────────────────
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.toast_overlay.set_child(main_box)

        # ── Header bar ───────────────────────────────────────────────────
        header = Adw.HeaderBar()
        main_box.append(header)

        # ── Content clamp ────────────────────────────────────────────────
        clamp = Adw.Clamp(maximum_size=600, margin_start=16, margin_end=16, margin_top=12, margin_bottom=12)
        main_box.append(clamp)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        clamp.set_child(content_box)

        # ── Title ────────────────────────────────────────────────────────
        title_label = Gtk.Label(label="Tracksheet Generator")
        title_label.add_css_class("title-1")
        content_box.append(title_label)

        subtitle_label = Gtk.Label(label="Select CSV job order reports to generate tracksheets")
        subtitle_label.add_css_class("dim-label")
        content_box.append(subtitle_label)

        # ── File list (scrolled) ─────────────────────────────────────────
        scroll = Gtk.ScrolledWindow(vexpand=True, min_content_height=200)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        content_box.append(scroll)

        self.file_list = Gtk.ListView()
        self.file_list.add_css_class("boxed-list")

        self.file_store = Gio.ListStore(item_type=Gtk.StringObject)
        self.selection = Gtk.MultiSelection(model=self.file_store)
        self.file_list.set_model(self.selection)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_factory_setup)
        factory.connect("bind", self._on_factory_bind)
        self.file_list.set_factory(factory)

        scroll.set_child(self.file_list)

        # ── Button bar ───────────────────────────────────────────────────
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        content_box.append(btn_box)

        add_btn = Gtk.Button(label="+ Add CSV Files")
        add_btn.add_css_class("suggested-action")
        add_btn.connect("clicked", self._on_add_files)
        btn_box.append(add_btn)

        remove_btn = Gtk.Button(label="Remove Selected")
        remove_btn.connect("clicked", self._on_remove_selected)
        btn_box.append(remove_btn)

        clear_btn = Gtk.Button(label="Clear All")
        clear_btn.connect("clicked", self._on_clear_all)
        btn_box.append(clear_btn)

        # ── Generate button ──────────────────────────────────────────────
        gen_btn = Gtk.Button(label="Generate Tracksheets")
        gen_btn.add_css_class("suggested-action")
        gen_btn.add_css_class("pill")
        gen_btn.set_halign(Gtk.Align.CENTER)
        gen_btn.set_size_request(260, -1)
        gen_btn.connect("clicked", self._on_generate)
        content_box.append(gen_btn)

        # ── Status bar ───────────────────────────────────────────────────
        self.status_label = Gtk.Label(label="No files selected")
        self.status_label.add_css_class("dim-label")
        self.status_label.add_css_class("caption")
        content_box.append(self.status_label)

        # ── Finalize ─────────────────────────────────────────────────────
        self.window.set_content(self.toast_overlay)
        self.window.present()

    # ── Factory callbacks ────────────────────────────────────────────────
    def _on_factory_setup(self, factory, list_item) -> None:
        label = Gtk.Label(xalign=0)
        label.add_css_class("body")
        list_item.set_child(label)

    def _on_factory_bind(self, factory, list_item) -> None:
        label = list_item.get_child()
        obj = list_item.get_item()
        label.set_text(obj.get_string())

    # ── Actions ──────────────────────────────────────────────────────────
    def _on_add_files(self, button) -> None:
        dialog = Gtk.FileDialog()
        dialog.set_title("Select CSV Files")

        csv_filter = Gtk.FileFilter()
        csv_filter.set_name("CSV files")
        csv_filter.add_pattern("*.csv")

        all_filter = Gtk.FileFilter()
        all_filter.set_name("All files")
        all_filter.add_pattern("*")

        filters = Gio.ListStore(item_type=Gtk.FileFilter)
        filters.append(csv_filter)
        filters.append(all_filter)
        dialog.set_filters(filters)

        dialog.open_multiple(self.window, None, self._on_files_selected)

    def _on_files_selected(self, dialog, result) -> None:
        try:
            files = dialog.open_multiple_finish(result)
        except GLib.Error:
            return

        for i in range(files.get_n_items()):
            gfile = files.get_item(i)
            path = Path(gfile.get_path())
            if path not in self.csv_paths:
                self.csv_paths.append(path)
                self.file_store.append(Gtk.StringObject.new(path.name))

        self._update_status()

    def _on_remove_selected(self, button) -> None:
        indices = []
        pos = self.selection.get_selection().get_minimum()
        while pos != -1:
            indices.append(pos)
            ok, pos = self.selection.get_selection().get_nth(pos + 1)

        for i in reversed(indices):
            self.file_store.remove(i)
            del self.csv_paths[i]

        self._update_status()

    def _on_clear_all(self, button) -> None:
        self.file_store.remove_all()
        self.csv_paths.clear()
        self._update_status()

    def _update_status(self) -> None:
        n = len(self.csv_paths)
        if n:
            self.status_label.set_text(f"{n} file{'s' if n != 1 else ''} selected")
        else:
            self.status_label.set_text("No files selected")

    def _on_generate(self, button) -> None:
        if not self.csv_paths:
            toast = Adw.Toast(title="Please add CSV files first.")
            toast.set_timeout(3)
            self.toast_overlay.add_toast(toast)
            return

        now = datetime.now()
        generated = []
        errors = []

        for csv_path in self.csv_paths:
            if not csv_path.exists():
                errors.append(f"{csv_path.name}: File not found")
                continue
            try:
                build_tracksheet(csv_path, now)
                generated.append(csv_path.stem)
            except Exception as e:
                errors.append(f"{csv_path.name}: {e}")

        if generated:
            toast = Adw.Toast(title=f"Generated {len(generated)} tracksheet(s)")
            toast.set_timeout(4)
            self.toast_overlay.add_toast(toast)

        if errors:
            dialog = Adw.MessageDialog(
                transient_for=self.window,
                heading="Errors",
                body="\n".join(errors),
            )
            dialog.add_response("ok", "OK")
            dialog.present()

        self.status_label.set_text(f"Last run: {len(generated)} generated, {len(errors)} errors")


def main() -> None:
    app = TracksheetApp()
    app.run(sys.argv)


if __name__ == "__main__":
    main()
