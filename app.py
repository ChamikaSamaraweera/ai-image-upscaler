import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import subprocess
import threading
import sys

class ImageScalerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Image Upscaler")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # If icon not found, continue without it

        self.selected_files = []
        self.output_folder = ""
        self.processing = False

        # Header with Info Button
        header_frame = tk.Frame(root, bg="#f0f0f0")
        header_frame.pack(pady=20, fill="x")

        header = tk.Label(header_frame, text="AI Image Upscaler", font=("Arial", 24, "bold"),
                          fg="#2c3e50", bg="#f0f0f0")
        header.pack(side="left", padx=20)

        # Info button (right side)
        info_btn = tk.Button(header_frame, text="ℹ️ Info", command=self.show_info,
                             bg="#3498db", fg="white", padx=15, pady=8,
                             font=("Arial", 10, "bold"), cursor="hand2", relief="flat")
        info_btn.pack(side="right", padx=20)

        # Top row - Image selector and Save location side by side
        top_frame = tk.Frame(root, bg="#f0f0f0")
        top_frame.pack(padx=20, pady=10, fill="both")

        # Left - Image selector section
        image_selector_frame = tk.LabelFrame(top_frame, text="Image Selector Section",
                                             padx=20, pady=20, font=("Arial", 11, "bold"),
                                             bg="white", relief="solid", borderwidth=2)
        image_selector_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Button(image_selector_frame, text="📁 Browse Images", command=self.select_files,
                  bg="#3498db", fg="white", padx=30, pady=15, font=("Arial", 11, "bold"),
                  cursor="hand2", relief="flat").pack(pady=10)

        self.file_label = tk.Label(image_selector_frame, text="No files selected",
                                   fg="#7f8c8d", font=("Arial", 10), bg="white", wraplength=300)
        self.file_label.pack(pady=10)

        # Right - Save location section
        save_location_frame = tk.LabelFrame(top_frame, text="Save Location Section",
                                            padx=20, pady=20, font=("Arial", 11, "bold"),
                                            bg="white", relief="solid", borderwidth=2)
        save_location_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Button(save_location_frame, text="📂 Select Output Folder", command=self.select_output,
                  bg="#2ecc71", fg="white", padx=30, pady=15, font=("Arial", 11, "bold"),
                  cursor="hand2", relief="flat").pack(pady=10)

        self.output_label = tk.Label(save_location_frame, text="Same as source folder",
                                     fg="#7f8c8d", font=("Arial", 10), bg="white", wraplength=300)
        self.output_label.pack(pady=10)

        # Middle - Upscale settings section (full width)
        upscale_settings_frame = tk.LabelFrame(root, text="Upscale Settings",
                                               padx=30, pady=25, font=("Arial", 11, "bold"),
                                               bg="white", relief="solid", borderwidth=2)
        upscale_settings_frame.pack(padx=20, pady=10, fill="both")

        # Model Selection
        model_frame = tk.Frame(upscale_settings_frame, bg="white")
        model_frame.pack(pady=8, fill="x")
        tk.Label(model_frame, text="AI Model:", width=18, anchor="w",
                 font=("Arial", 10, "bold"), bg="white").pack(side="left")
        self.model_var = tk.StringVar(value="realesrgan-x4plus")

        self.models_info = {
            "realesrgan-x4plus": ("Real-ESRGAN x4plus (General)", ["2", "3", "4"]),
            "realesrgan-x4plus-anime": ("Real-ESRGAN x4plus Anime", ["2", "3", "4"]),
            "realesr-animevideov3": ("Real-ESR AnimeVideo v3", ["2", "3", "4"]),
            "realesrnet-x4plus": ("Real-ESRNet x4plus", ["4"])
        }

        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var,
                                   values=list(self.models_info.keys()),
                                   width=30, state="readonly", font=("Arial", 10))
        model_combo.pack(side="left", padx=10)
        model_combo.bind("<<ComboboxSelected>>", self.update_scale_options)

        # Upscale Factor
        outscale_frame = tk.Frame(upscale_settings_frame, bg="white")
        outscale_frame.pack(pady=8, fill="x")
        tk.Label(outscale_frame, text="Upscale Factor:", width=18, anchor="w",
                 font=("Arial", 10, "bold"), bg="white").pack(side="left")
        self.outscale_var = tk.StringVar(value="4")
        self.outscale_combo = ttk.Combobox(outscale_frame, textvariable=self.outscale_var,
                                           values=["2", "3", "4"], width=15, state="readonly",
                                           font=("Arial", 10))
        self.outscale_combo.pack(side="left", padx=10)
        tk.Label(outscale_frame, text="x", fg="#7f8c8d", font=("Arial", 10, "bold"),
                 bg="white").pack(side="left", padx=5)

        # Output Format
        format_frame = tk.Frame(upscale_settings_frame, bg="white")
        format_frame.pack(pady=8, fill="x")
        tk.Label(format_frame, text="Output Format:", width=18, anchor="w",
                 font=("Arial", 10, "bold"), bg="white").pack(side="left")
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                    values=["png", "jpg", "webp"], width=15, state="readonly",
                                    font=("Arial", 10))
        format_combo.pack(side="left", padx=10)

        # Progress Bar Section
        progress_container = tk.Frame(root, bg="#f0f0f0")
        progress_container.pack(padx=20, pady=15, fill="x")

        tk.Label(progress_container, text="Progressbar", font=("Arial", 10),
                 bg="#f0f0f0", fg="#7f8c8d").pack(anchor="w", padx=5)

        self.progress_bar = ttk.Progressbar(progress_container, mode='determinate',
                                            style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", pady=5)

        self.progress_percent = tk.Label(progress_container, text="0%",
                                         font=("Arial", 9, "bold"), bg="#f0f0f0", fg="#3498db")
        self.progress_percent.pack(anchor="e", padx=5)

        self.status_label = tk.Label(progress_container, text="Ready", fg="#7f8c8d",
                                     font=("Arial", 9), bg="#f0f0f0", anchor="w")
        self.status_label.pack(fill="x", padx=5)

        # Bottom - Upscale Button (right aligned)
        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack(padx=20, pady=20, fill="x")

        self.submit_btn = tk.Button(button_frame, text="Upscale Button",
                                    command=self.start_upscaling,
                                    bg="#e74c3c", fg="white", padx=60, pady=15,
                                    font=("Arial", 12, "bold"), cursor="hand2", relief="flat")
        self.submit_btn.pack(side="right")

        # Copyright Footer
        footer_frame = tk.Frame(root, bg="#2c3e50", height=60)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)

        # Developer info
        dev_label = tk.Label(footer_frame, text="Developed by Chamika Samaraweera | Teaminfinity.lk",
                             font=("Arial", 9), bg="#2c3e50", fg="white")
        dev_label.pack(side="left", padx=20, pady=15)

        # Separator
        separator = tk.Label(footer_frame, text="|", font=("Arial", 9),
                             bg="#2c3e50", fg="#7f8c8d")
        separator.pack(side="left", padx=5)

        # Real-ESRGAN copyright
        tech_label = tk.Label(footer_frame, text="Powered by Real-ESRGAN",
                              font=("Arial", 9), bg="#2c3e50", fg="#95a5a6")
        tech_label.pack(side="left", padx=5)

        # Version
        version_label = tk.Label(footer_frame, text="v1.2",
                                 font=("Arial", 8), bg="#2c3e50", fg="#7f8c8d")
        version_label.pack(side="right", padx=20)

        # Configure progress bar style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor='#ecf0f1',
                        background='#3498db',
                        thickness=25)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All files", "*.*")]
        )
        if files:
            self.selected_files = list(files)
            file_names = "\n".join([os.path.basename(f) for f in files[:3]])
            if len(files) > 3:
                file_names += f"\n... and {len(files) - 3} more"
            self.file_label.config(text=f"{len(files)} file(s) selected:\n{file_names}")

    def show_info(self):
        """Display developer and application information"""
        info_window = tk.Toplevel(self.root)
        info_window.title("About - AI Image Upscaler")
        info_window.geometry("550x550")
        info_window.resizable(False, False)
        info_window.configure(bg="white")

        # Center the window
        info_window.transient(self.root)
        info_window.grab_set()

        # Icon/Title
        title_frame = tk.Frame(info_window, bg="#3498db", height=80)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="🚀", font=("Arial", 30), bg="#3498db").pack(pady=2)
        tk.Label(title_frame, text="AI Image Upscaler", font=("Arial", 16, "bold"),
                 bg="#3498db", fg="white").pack()

        # Content frame
        content_frame = tk.Frame(info_window, bg="white", padx=30, pady=20)
        content_frame.pack(fill="both", expand=True)

        # Version
        tk.Label(content_frame, text="Version 1.0", font=("Arial", 11),
                 bg="white", fg="#7f8c8d").pack(pady=5)

        # Separator
        separator1 = tk.Frame(content_frame, height=2, bg="#ecf0f1")
        separator1.pack(fill="x", pady=10)

        # Developer Info
        tk.Label(content_frame, text="Developer", font=("Arial", 10, "bold"),
                 bg="white", fg="#2c3e50").pack(anchor="w", pady=(10, 5))
        tk.Label(content_frame, text="Chamika Samaraweera (Teaminfinity.lk)", font=("Arial", 10),
                 bg="white", fg="#34495e").pack(anchor="w", padx=10)

        # Separator
        separator2 = tk.Frame(content_frame, height=2, bg="#ecf0f1")
        separator2.pack(fill="x", pady=10)

        # Technology
        tk.Label(content_frame, text="Powered By", font=("Arial", 10, "bold"),
                 bg="white", fg="#2c3e50").pack(anchor="w", pady=(10, 5))
        tk.Label(content_frame, text="Real-ESRGAN", font=("Arial", 10),
                 bg="white", fg="#34495e").pack(anchor="w", padx=10)
        tk.Label(content_frame, text="AI-based Image Super-Resolution",
                 font=("Arial", 9, "italic"), bg="white", fg="#95a5a6").pack(anchor="w", padx=10)

        # Separator
        separator3 = tk.Frame(content_frame, height=2, bg="#ecf0f1")
        separator3.pack(fill="x", pady=10)

        # Description
        tk.Label(content_frame, text="About", font=("Arial", 10, "bold"),
                 bg="white", fg="#2c3e50").pack(anchor="w", pady=(10, 5))
        desc_text = "Enhance your images using advanced AI\nupscaling technology. Supports 2x, 3x,\nand 4x upscaling with multiple AI models."
        tk.Label(content_frame, text=desc_text, font=("Arial", 9),
                 bg="white", fg="#34495e", justify="left").pack(anchor="w", padx=10)

        # Close button
        tk.Button(info_window, text="Close", command=info_window.destroy,
                  bg="#e74c3c", fg="white", padx=40, pady=10,
                  font=("Arial", 10, "bold"), cursor="hand2", relief="flat").pack(pady=15)

    def update_scale_options(self, event=None):
        """Update available scale options based on selected model"""
        model = self.model_var.get()
        if model in self.models_info:
            available_scales = self.models_info[model][1]
            self.outscale_combo.config(values=available_scales)
            self.outscale_var.set(available_scales[-1])

    def select_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_label.config(text=f"Saving to:\n{folder}")

    def start_upscaling(self):
        if self.processing:
            messagebox.showwarning("Processing", "Already processing images!")
            return

        if not self.selected_files:
            messagebox.showerror("Error", "Please select images first!")
            return

        thread = threading.Thread(target=self.process_images)
        thread.daemon = True
        thread.start()

    def process_images(self):
        self.processing = True
        self.submit_btn.config(state="disabled", bg="#95a5a6")

        # Reset progress
        self.progress_bar['value'] = 0
        self.progress_percent.config(text="0%")

        outscale = self.outscale_var.get()
        model = self.model_var.get()
        output_format = self.format_var.get()

        success_count = 0
        total = len(self.selected_files)

        for idx, file_path in enumerate(self.selected_files, 1):
            try:
                # Update progress bar with animation
                progress = int((idx / total) * 100)
                self.animate_progress(progress)
                self.progress_percent.config(text=f"{progress}%")
                self.status_label.config(text=f"Processing {idx}/{total}: {os.path.basename(file_path)}")

                if self.output_folder:
                    output_dir = self.output_folder
                else:
                    output_dir = os.path.dirname(file_path)

                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(output_dir, f"{name}_upscaled.{output_format}")

                script_dir = os.path.dirname(os.path.abspath(__file__))
                realesrgan_path = os.path.join(script_dir, "realesrgan-ncnn-vulkan.exe")

                if not os.path.exists(realesrgan_path):
                    raise FileNotFoundError(f"realesrgan-ncnn-vulkan.exe not found at: {realesrgan_path}")

                cmd = [
                    realesrgan_path,
                    "-i", file_path,
                    "-o", output_path,
                    "-s", outscale,
                    "-n", model,
                    "-f", output_format
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    success_count += 1
                else:
                    print(f"Error processing {filename}: {result.stderr}")

            except Exception as e:
                print(f"Exception processing {os.path.basename(file_path)}: {str(e)}")

        # Complete animation to 100%
        self.animate_progress(100)
        self.progress_percent.config(text="100%")
        self.status_label.config(text=f"Complete! {success_count}/{total} images upscaled")
        self.submit_btn.config(state="normal", bg="#e74c3c")
        self.processing = False

        messagebox.showinfo("Complete", f"Successfully upscaled {success_count}/{total} image(s)!")
        self.selected_files = []
        self.file_label.config(text="No files selected")

        # Reset progress bar after 2 seconds
        self.root.after(2000, lambda: [self.progress_bar.config(value=0),
                                       self.progress_percent.config(text="0%"),
                                       self.status_label.config(text="Ready")])

    def animate_progress(self, target_value):
        """Smoothly animate progress bar to target value"""
        current = self.progress_bar['value']
        if current < target_value:
            step = 1
            while current < target_value:
                current += step
                if current > target_value:
                    current = target_value
                self.progress_bar['value'] = current
                self.root.update_idletasks()
                self.root.after(5)  # Small delay for smooth animation

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageScalerApp(root)
    root.mainloop()