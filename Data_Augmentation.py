import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageEnhance, ImageFilter, ImageTk
import cv2
import random
import numpy as np
import subprocess
import threading

# دالة لاختيار ملف الفيديو أو الصورة
# دالة لاختيار ملف الفيديو أو الصورة
def choose_source_file():
    file = filedialog.askopenfilename(
        title="اختر ملف الفيديو أو الصورة",
        filetypes=(("All Files", "*.*"), ("Images", "*.png;*.jpg;*.jpeg;*.webp;*.gif"), ("Videos", "*.mp4;*.avi;*.mov"))
    )
    source_file_var.set(file)

# دالة لاختيار مسار الحفظ
def choose_destination_folder():
    folder = filedialog.askdirectory(title="اختر المجلد لحفظ الملفات الناتجة")
    destination_folder_var.set(folder)

# دالة لتنفيذ العملية باستخدام الخيوط
def process_files():
    source_file = source_file_var.get()
    destination_folder = destination_folder_var.get()
    num_files = num_files_var.get()

    if not source_file or not destination_folder or not num_files.isdigit() or int(num_files) <= 0:
        messagebox.showerror("خطأ", "يرجى إدخال جميع البيانات بشكل صحيح.")
        return

    num_files = int(num_files)
    base_name, ext = os.path.splitext(os.path.basename(source_file))
    output_dir = os.path.join(destination_folder, base_name)

    # إنشاء المجلد الناتج
    os.makedirs(output_dir, exist_ok=True)

    # بدء الخيط في معالجة الملفات
    progress_bar['value'] = 0
    progress_bar['maximum'] = num_files

    threading.Thread(target=start_processing, args=(source_file, output_dir, num_files, ext)).start()

# دالة تنفيذ عملية المعالجة
def start_processing(source_file, output_dir, num_files, ext):
    try:
        if ext.lower() in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
            process_images(source_file, output_dir, num_files)
        elif ext.lower() in [".mp4", ".avi", ".mov"]:
            process_videos(source_file, output_dir, num_files)
        else:
            messagebox.showerror("خطأ", "صيغة الملف غير مدعومة.")
            return
        messagebox.showinfo("نجاح", "تمت العملية بنجاح!")
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ أثناء المعالجة: {str(e)}")
    finally:
        progress_bar['value'] = 0

# معالجة الصور باستخدام تقنيات تعزيز البيانات المتقدمة
def process_images(source_file, output_dir, num_files):
    image = Image.open(source_file)
    for i in range(1, num_files + 1):
        augmented_image = augment_image(image)
        output_file = os.path.join(output_dir, f"{i}{os.path.splitext(source_file)[1]}")
        augmented_image.save(output_file)
        progress_bar['value'] = i
        root.update_idletasks()

# تقنيات تعزيز البيانات المتقدمة للصور
def augment_image(image):
    # 1. تغيير السطوع
    brightness = random.uniform(0.7, 1.5)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)

    # 2. تغيير التباين
    contrast = random.uniform(0.7, 1.5)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)

    # 3. إضافة الضبابية
    if random.choice([True, False]):
        image = image.filter(ImageFilter.GaussianBlur(random.uniform(1, 3)))

    # 4. قص الصورة بشكل عشوائي
    width, height = image.size
    crop_x = random.randint(0, int(width * 0.1))
    crop_y = random.randint(0, int(height * 0.1))
    image = image.crop((crop_x, crop_y, width - crop_x, height - crop_y))

    # 5. تدوير الصورة بشكل عشوائي
    angle = random.randint(-30, 30)
    image = image.rotate(angle)

    # 6. إضافة ضوضاء عشوائية
    if random.choice([True, False]):
        np_image = np.array(image)
        noise = np.random.normal(0, 25, np_image.shape)
        np_image = np.clip(np_image + noise, 0, 255)
        image = Image.fromarray(np_image.astype('uint8'))

    return image

# معالجة الفيديوهات باستخدام تقنيات تعزيز البيانات المتقدمة
def process_videos(source_file, output_dir, num_files, compression='mp4v'):
    cap = cv2.VideoCapture(source_file)
    if not cap.isOpened():
        messagebox.showerror("خطأ", "تعذر فتح ملف الفيديو.")
        return

    # معلومات الفيديو
    fps = int(cap.get(cv2.CAP_PROP_FPS)) // 2  # تقليل معدل الإطارات إلى نصف القيمة الأصلية
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2  # تقليل العرض إلى النصف
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2  # تقليل الارتفاع إلى النصف

    # تحديد الترميز
    fourcc = cv2.VideoWriter_fourcc(*compression)  # ترميز الفيديو

    for i in range(1, num_files + 1):
        output_file = os.path.join(output_dir, f"{i}.mp4")
        
        # استخدام subprocess و ffmpeg لضغط الفيديو بعد المعالجة
        try:
            # إعدادات ffmpeg لضغط الفيديو وتحسين جودته
            command = [
                'ffmpeg', 
                '-y',  # الكتابة فوق الملف إذا كان موجودًا
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-pix_fmt', 'bgr24',  # تنسيق البكسل الخاص بالفيديو
                '-s', f'{width}x{height}',  # تحديد حجم الفيديو
                '-r', str(fps),  # معدل الإطارات
                '-i', '-',  # إدخال من stdin
                '-vcodec', 'libx264',  # استخدام H.264
                '-crf', '23',  # تحديد جودة الفيديو (كلما زادت القيمة، انخفضت الجودة وحجم الملف)
                '-preset', 'medium',  # تحسين الضغط (بسرعة متوسطة للحصول على توازن بين الجودة والسرعة)
                '-pix_fmt', 'yuv420p',  # صيغة الألوان المدعومة
                '-tune', 'film',  # تخصيص الضغط للأفلام (لتقليل التشويش)
                output_file  # ملف الإخراج
            ]
            
            # استدعاء subprocess
            process = subprocess.Popen(command, stdin=subprocess.PIPE)

            # إعادة ضبط موضع الإطارات
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # اختيار التأثيرات الثابتة لكل فيديو
            brightness_factor = random.uniform(0.8, 1.2)
            rotation_angle = random.uniform(-5, 5)
            blur_strength = random.uniform(0.5, 1.5)
            noise_strength = random.uniform(0, 10)  # تقليل قوة الضوضاء لتقليل التشويش

            # التأثيرات الثابتة لهذا الفيديو
            selected_effects = [
                lambda frame: apply_brightness(frame, brightness_factor),
                lambda frame: apply_rotation(frame, rotation_angle),
                lambda frame: apply_blur(frame, blur_strength),
                lambda frame: apply_noise(frame, noise_strength)  # تقليل الضوضاء
            ]

            # معالجة الإطارات وكتابة البيانات عبر stdin إلى ffmpeg
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # تغيير حجم الإطار لتقليل الحجم
                frame = cv2.resize(frame, (width, height))

                # تطبيق التأثيرات المختارة
                for effect in selected_effects:
                    frame = effect(frame)

                # إرسال الإطار إلى ffmpeg عبر stdin
                process.stdin.write(frame.tobytes())

            # إغلاق stdin وإتمام العملية
            process.stdin.close()
            process.wait()  # الانتظار حتى ينتهي subprocess من معالجة الفيديو
            progress_bar['value'] = i
            root.update_idletasks()

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء ضغط الفيديو: {str(e)}")
            continue

    cap.release()
    cv2.destroyAllWindows()


# دوال التأثيرات
def apply_brightness(frame, brightness_factor):
    """
    تطبيق تأثير السطوع على إطار معين.
    
    Args:
        frame (numpy.ndarray): الإطار المطلوب تعديل السطوع عليه.
        brightness_factor (float): عامل السطوع (بين 0.8 و 1.2 مثلاً).
        
    Returns:
        numpy.ndarray: الإطار بعد تطبيق تأثير السطوع.
    """
    return cv2.convertScaleAbs(frame, alpha=brightness_factor, beta=0)

def apply_rotation(frame, angle):
    """
    تطبيق تأثير التدوير على إطار معين.

    Args:
        frame (numpy.ndarray): الإطار المطلوب تدويره.
        angle (float): زاوية التدوير بالدرجات (مثل -5 إلى 5).
        
    Returns:
        numpy.ndarray: الإطار بعد التدوير.
    """
    h, w = frame.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    cos = abs(M[0, 0])
    sin = abs(M[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    rotated = cv2.warpAffine(frame, M, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

    x = (new_w - w) // 2
    y = (new_h - h) // 2
    cropped = rotated[y:y + h, x:x + w]

    return cropped

def apply_blur(frame, strength):
    """
    تطبيق تأثير التمويه (Blur) على إطار معين.
    
    Args:
        frame (numpy.ndarray): الإطار المطلوب تطبيق التأثير عليه.
        strength (float): قوة التمويه (عشوائية بين الفيديوهات).
        
    Returns:
        numpy.ndarray: الإطار بعد تطبيق تأثير التمويه.
    """
    return cv2.GaussianBlur(frame, (5, 5), strength)

def apply_noise(frame, noise_strength):
    """
    تطبيق تأثير الضوضاء (Noise) على إطار معين.
    
    Args:
        frame (numpy.ndarray): الإطار المطلوب إضافة الضوضاء عليه.
        noise_strength (float): قوة الضوضاء (عشوائية بين الفيديوهات).
        
    Returns:
        numpy.ndarray: الإطار بعد إضافة الضوضاء.
    """
    noise = np.random.normal(0, noise_strength, frame.shape)
    noisy_frame = np.clip(frame + noise, 0, 255)
    return noisy_frame.astype('uint8')

# تقنيات تعزيز البيانات المتقدمة للفيديوهات
def augment_frame(frame):
    # لا حاجة لتطبيق كل تقنية على كل إطار بشكل منفصل
    return frame  # نعيد الإطار كما هو (يتم تطبيق التأثيرات على الفيديو ككل وليس كل إطار)


# إعداد واجهة المستخدم الرسومية
root = tk.Tk()
root.title("برنامج تعزيز البيانات")
root.geometry("1100x650")  # تحديد حجم الواجهة
root.resizable(width=False, height=False)  # تعيين قابلية التكبير والتصغير إلى القيمة False

# تحديد المسار الصحيح للملفات عند تشغيل التطبيق بشكل مستقل
def resource_path(relative_path):
    """تحديد المسار للملفات المضمنة عند استخدام PyInstaller
    pyinstaller --onefile --noconsole --add-data "logo.ico;." --add-data "AI.jpg;." --icon=logo.ico Data_Augmentation.py
    """
    try:
        # إذا كان التطبيق يعمل من داخل PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # إذا كان يعمل في بيئة التطوير
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# تعيين الأيقونة للتطبيق إذا كانت موجودة
icon_path = resource_path("logo.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# إضافة صورة خلفية إذا كانت موجودة
background_path = resource_path("AI.jpg")
if os.path.exists(background_path):
    background_image = Image.open(background_path)  # فتح صورة الخلفية
    background_image = background_image.resize((1100, 650), Image.BICUBIC)  # تغيير حجم الصورة
    background_photo = ImageTk.PhotoImage(background_image)  # تحويل الصورة إلى PhotoImage لعرضها في Tkinter
    background_label = tk.Label(root, image=background_photo)  # إنشاء علامة (Label) لعرض الصورة
    background_label.place(x=0, y=0, relwidth=1, relheight=1)  # تحديد مكان وحجم الصورة في النافذة

# الحصول على حجم الشاشة
screen_width = root.winfo_screenwidth()

# حساب موقع النافذة المركزية
x_position = (screen_width - 1100) // 2
y_position = 0

# تحديد موقع النافذة المركزية
root.geometry(f"1100x650+{x_position}+{y_position}")

# متغيرات لحفظ المدخلات
source_file_var = tk.StringVar()
destination_folder_var = tk.StringVar()
num_files_var = tk.StringVar()


# إنشاء مكان لعرض لتقسيم الواجهة  
fram = tk.Label(root)  # تعيين خلفية شفافة للإطار
fram.pack(pady=3)

# تسميات ومربعات الإدخال
tk.Label(fram, text="اختر ملف الفيديو أو الصورة الأصلية").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(fram, textvariable=source_file_var, width=90).grid(row=1, column=0, padx=10, pady=10)
tk.Button(fram, text="اختيار ملف", font=("Helvetica", 14), command=choose_source_file, width=10, height=1, bg="#3498db", fg="white").grid(row=1, column=1, padx=10, pady=10)

tk.Label(fram, text="حدد المجلد الذي تريد حفظ الملفات الناتجة فيه").grid(row=2, column=0, padx=10, pady=10)
tk.Entry(fram, textvariable=destination_folder_var, width=90).grid(row=3, column=0, padx=10, pady=10)
tk.Button(fram, text="اختيار مسار", command=choose_destination_folder, font=("Helvetica", 14), width=10, height=1, bg="#e67e22", fg="white").grid(row=3, column=1, padx=10, pady=10)

tk.Label(fram, text="أدخل عدد الملفات المطلوب توليدها").grid(row=4, column=0, padx=10, pady=10)
tk.Entry(fram, textvariable=num_files_var, width=25).grid(row=5, column=0, padx=10, pady=10)

# زر التحويل
tk.Label(fram, text="إضغط بدء العملية وإنتظر ...").grid(row=6, column=0, padx=10, pady=10)
tk.Button(fram, text="بدء العملية", command=process_files, font=("Helvetica", 14), width=25, height=1, bg="#2ecc71", fg="white").grid(row=7, column=0, padx=10, pady=20)

# شريط التقدم
progress_bar = ttk.Progressbar(fram, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=8, column=0, columnspan=3, padx=10, pady=20)

# إضافة شريط في أسفل الواجهة (Footer)
footer_label = tk.Label(root, text="تم التطوير بواسطة م/ صفوان سعدان", font=("Helvetica", 15), bg="#2c3e50", fg="white")
footer_label.pack(side="bottom", fill="x", pady=2)

# بدء التطبيق
root.mainloop()