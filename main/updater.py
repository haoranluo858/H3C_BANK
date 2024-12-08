import os
import requests
import shutil
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

class UpdaterApp:
    def __init__(self, root, download_url, target_path):
        self.root = root
        self.download_url = download_url
        self.target_path = target_path

        self.root.title("更新程序")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        tk.Label(self.root, text="正在更新，请稍候...", font=("Helvetica", 14)).pack(pady=20)
        
        # 创建进度条
        self.progress = ttk.Progressbar(self.root, length=300, mode="determinate")
        self.progress.pack(pady=20)
        
        # 状态标签
        self.status_label = tk.Label(self.root, text="", font=("Helvetica", 10))
        self.status_label.pack(pady=10)
        
        # 开始下载
        self.root.after(100, self.start_download)

    def start_download(self):
        """启动下载流程"""
        try:
            temp_path = self.download_with_progress()
            self.replace_and_restart(temp_path)
        except Exception as e:
            messagebox.showerror("更新失败", f"更新失败：{e}")
            self.root.quit()

    def download_with_progress(self):
        """下载文件并更新进度条"""
        response = requests.get(self.download_url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        temp_path = f"{self.target_path}.new"
        downloaded_size = 0

        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # 更新进度条
                    progress_percent = (downloaded_size / total_size) * 100
                    self.progress["value"] = progress_percent
                    self.status_label.config(text=f"下载进度: {progress_percent:.2f}%")
                    self.root.update_idletasks()
        self.status_label.config(text="下载完成，正在替换旧版本...")
        return temp_path

    def replace_and_restart(self, temp_path):
        """替换旧版本并启动新版本"""
        if os.path.exists(self.target_path):
            os.remove(self.target_path)  # 删除旧版本
        shutil.move(temp_path, self.target_path)  # 替换为新版本

        self.status_label.config(text="更新完成，正在启动新版本...")
        self.root.update_idletasks()

        # 启动新版本
        subprocess.Popen([self.target_path], shell=True)
        self.root.quit()

def main():
    if len(sys.argv) < 5 or sys.argv[1] != "--target" or sys.argv[3] != "--url":
        print("用法: updater.exe --target <目标路径> --url <下载链接>")
        return

    target_path = sys.argv[2]
    download_url = sys.argv[4]

    root = tk.Tk()
    app = UpdaterApp(root, download_url, target_path)
    root.mainloop()

if __name__ == "__main__":
    main()
