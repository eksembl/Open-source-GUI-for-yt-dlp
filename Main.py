import yt_dlp, customtkinter, os, static_ffmpeg, threading, traceback

customtkinter.set_appearance_mode("system")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1000x600")
        self.title("Trust Downloader")
        self.resizable(False, False)

        self.download_path = os.getcwd()

        static_ffmpeg.add_paths()

        self.url_entry = customtkinter.CTkEntry(
            self,
            placeholder_text="Paste URL here...",
            width=450,
            height=35
        )
        self.url_entry.place(relx=0.5, rely=0.2, anchor="center")

        self.folder_btn = customtkinter.CTkButton(
            self,
            text=f"Save to: {os.path.basename(self.download_path)}",
            command=self.select_folder,
            width=450
        )
        self.folder_btn.place(relx=0.5, rely=0.30, anchor="center")

        self.download_btn = customtkinter.CTkButton(
            self,
            text="Download Video",
            command=self.start_download_thread,
            width=300,
            height=40
        )
        self.download_btn.place(relx=0.5, rely=0.40, anchor="center")

        self.progress = customtkinter.CTkProgressBar(self, width=500)
        self.progress.place(relx=0.5, rely=0.47, anchor="center")
        self.progress.set(0)

        self.format_var = customtkinter.StringVar(value="Mp4")
        self.format_menu = customtkinter.CTkOptionMenu(
            self,
            values=["Mp4", "Mp3"],
            variable=self.format_var
        )
        self.format_menu.place(relx=0.58, rely=0.55, anchor="center")

        self.quality_var = customtkinter.StringVar(value="1080p")
        self.quality_menu = customtkinter.CTkOptionMenu(
            self,
            values=["1440p", "1080p", "720p", "480p"],
            variable=self.quality_var
        )
        self.quality_menu.place(relx=0.42, rely=0.55, anchor="center")

    def select_folder(self):
        folder = customtkinter.filedialog.askdirectory()
        if folder:
            self.download_path = folder
            self.folder_btn.configure(text=f"Save to: {os.path.basename(folder)}")

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url.startswith(("http://", "https://")):
            return

        self.progress.set(0)
        self.download_btn.configure(state="disabled", text="Downloading...")

        threading.Thread(
            target=self.run_download_process,
            args=(url, self.format_var.get(), self.quality_var.get(), self.download_path),
            daemon=True
        ).start()

    def update_progress(self, value):
        self.progress.set(value)

    def finish_download(self, success):
        self.download_btn.configure(
            state="normal",
            text="Finished" if success else "Error / Retry"
        )

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                self.after(0, self.update_progress, downloaded / total)
        elif d['status'] == 'finished':
            self.after(0, self.update_progress, 1)

    def run_download_process(self, url, fmt, quality, path):
        try:
            path_opts = {'home': path}

            if fmt == "Mp3":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'paths': path_opts,
                    'progress_hooks': [self.progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                height = quality.replace("p", "")
                ydl_opts = {
                    'format': f'bestvideo[height<={height}]+bestaudio/best',
                    'merge_output_format': 'mp4',
                    'paths': path_opts,
                    'progress_hooks': [self.progress_hook],
                }

            ydl_opts.update({
                'quiet': True,
                'noprogress': True,
            })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.after(0, self.finish_download, True)

        except Exception:
            traceback.print_exc()
            self.after(0, self.finish_download, False)


if __name__ == "__main__":
    app = App()
    app.mainloop()
