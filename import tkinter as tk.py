import os
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from tkcalendar import Calendar
from tkinter import ttk

def split_video(input_file, segments, date):
    date_folder = f"segments_{date}"
    output_folder = os.path.join(os.path.dirname(input_file), date_folder)
    os.makedirs(output_folder, exist_ok=True)

    video_duration = get_video_duration(input_file)

    for start_time, end_time, segment_name in segments:
        if start_time >= end_time:
            raise ValueError(f"El tiempo de corte de fin ({end_time}) debe ser mayor que el tiempo de inicio ({start_time}).")
        if end_time > video_duration:
            raise ValueError(f"El tiempo de corte de fin ({end_time}) excede la duración del video ({video_duration}).")
        
        # Format the output filename safely for Windows
        output_name = f"[{date}] {segment_name}.mp4".replace("/", "-").replace("\\", "-")
        output_path = os.path.join(output_folder, output_name)
        
        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-ss", str(start_time),
            "-to", str(end_time),
            "-c", "copy",
            output_path
        ]
        subprocess.run(cmd, check=True)

def get_video_duration(input_file):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.mov;*.avi")])
    if filename:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, filename)

def select_date():
    def set_date():
        selected_date = cal.get_date()
        entry_custom_date.delete(0, tk.END)
        entry_custom_date.insert(0, selected_date)
        top.destroy()

    top = tk.Toplevel(root)
    top.title("Seleccionar Fecha")
    cal = Calendar(top, selectmode="day")
    cal.pack(padx=10, pady=10)
    btn_select = ttk.Button(top, text="Seleccionar", command=set_date)
    btn_select.pack(pady=10)

def start_process():
    input_file = entry_file_path.get()
    segments = []
    
    try:
        for i in range(len(start_time_entries)):
            start_hours = int(start_time_entries[i][0].get())
            start_minutes = int(start_time_entries[i][1].get())
            start_seconds = int(start_time_entries[i][2].get())
            start_time = start_hours * 3600 + start_minutes * 60 + start_seconds
            
            end_hours = int(end_time_entries[i][0].get())
            end_minutes = int(end_time_entries[i][1].get())
            end_seconds = int(end_time_entries[i][2].get())
            end_time = end_hours * 3600 + end_minutes * 60 + end_seconds
            
            segment_name = segment_name_entries[i].get().strip()
            if not segment_name:
                raise ValueError("Todos los segmentos deben tener un nombre.")
            
            segments.append((start_time, end_time, segment_name))
        
        date = entry_custom_date.get() if entry_custom_date.get() else datetime.now().strftime("%Y-%m-%d")
        split_video(input_file, segments, date)
        messagebox.showinfo("Éxito", "El video ha sido cortado y guardado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_segment_entry():
    row = len(start_time_entries) + 3

    start_frame = ttk.Frame(root)
    start_frame.grid(row=row, column=0, columnspan=1, padx=5, pady=5)
    ttk.Label(start_frame, text="Inicio").pack(side=tk.LEFT)
    
    start_hours_spinbox = ttk.Spinbox(start_frame, from_=0, to=23, width=3)
    start_hours_spinbox.pack(side=tk.LEFT)
    
    start_minutes_spinbox = ttk.Spinbox(start_frame, from_=0, to=59, width=3)
    start_minutes_spinbox.pack(side=tk.LEFT)
    
    start_seconds_spinbox = ttk.Spinbox(start_frame, from_=0, to=59, width=3)
    start_seconds_spinbox.pack(side=tk.LEFT)
    
    start_time_entries.append((start_hours_spinbox, start_minutes_spinbox, start_seconds_spinbox))
    
    end_frame = ttk.Frame(root)
    end_frame.grid(row=row, column=1, columnspan=1, padx=5, pady=5)
    ttk.Label(end_frame, text="Fin").pack(side=tk.LEFT)
    
    end_hours_spinbox = ttk.Spinbox(end_frame, from_=0, to=23, width=3)
    end_hours_spinbox.pack(side=tk.LEFT)
    
    end_minutes_spinbox = ttk.Spinbox(end_frame, from_=0, to=59, width=3)
    end_minutes_spinbox.pack(side=tk.LEFT)
    
    end_seconds_spinbox = ttk.Spinbox(end_frame, from_=0, to=59, width=3)
    end_seconds_spinbox.pack(side=tk.LEFT)
    
    end_time_entries.append((end_hours_spinbox, end_minutes_spinbox, end_seconds_spinbox))
    
    segment_name_entry = ttk.Entry(root)
    segment_name_entry.grid(row=row, column=2, padx=5, pady=5)
    segment_name_entries.append(segment_name_entry)
    
    delete_button = ttk.Button(root, text="Eliminar", command=lambda row=row: delete_segment_entry(row))
    delete_button.grid(row=row, column=3, padx=5, pady=5)
    
    segment_widgets.append((start_frame, end_frame, segment_name_entry, delete_button))
    
    if row == 4:
        btn_add_segment.grid(row=row + 1, columnspan=4, pady=10, sticky='ne', padx=(0, 10))
    else:
        btn_add_segment.grid(row=row + 1, columnspan=4, pady=5, sticky='ne', padx=(0, 10))

def delete_segment_entry(row):
    idx = row - 4

    start_time_entries.pop(idx)
    end_time_entries.pop(idx)
    segment_name_entries.pop(idx)
    
    for widget in segment_widgets[idx]:
        widget.destroy()
    
    segment_widgets.pop(idx)
    refresh_segment_entries()

def refresh_segment_entries():
    # Recuperar el índice de la última fila donde se agregarán nuevos segmentos
    last_row = max(4, len(start_time_entries) + 3)
    
    # Eliminar solo los widgets relacionados con los segmentos
    for widget in segment_widgets:
        widget[0].grid_forget()
        widget[1].grid_forget()
        widget[2].grid_forget()
        widget[3].grid_forget()
    
    # Volver a colocar los segmentos restantes
    for i, (start_time_entry, end_time_entry, segment_name_entry, delete_button) in enumerate(segment_widgets, start=3):
        start_time_entry.grid(row=i, column=0, columnspan=1, padx=5, pady=5)
        end_time_entry.grid(row=i, column=1, columnspan=1, padx=5, pady=5)
        segment_name_entry.grid(row=i, column=2, padx=5, pady=5)
        delete_button.grid(row=i, column=3, padx=5, pady=5)

    btn_add_segment.grid(row=last_row + 1, columnspan=4, pady=10, sticky='ne', padx=(0, 10))

root = tk.Tk()
root.title("Corte de Video")

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 10))
style.configure('TLabel', font=('Helvetica', 10))
style.configure('TEntry', font=('Helvetica', 10))
style.configure('TSpinbox', font=('Helvetica', 10))

tk.Label(root, text="Ruta del archivo:").grid(row=0, column=0, padx=5, pady=5)
entry_file_path = ttk.Entry(root, width=50)
entry_file_path.grid(row=0, column=1, padx=5, pady=5)
btn_browse = ttk.Button(root, text="Buscar", command=browse_file)
btn_browse.grid(row=0, column=2, padx=5, pady=5)

btn_start = ttk.Button(root, text="Iniciar Proceso", command=start_process)
btn_start.grid(row=0, column=3, padx=5, pady=5, sticky='e')

ttk.Label(root, text="Hora Minuto Segundo").grid(row=2, column=0, padx=5, pady=5)
ttk.Label(root, text="Hora Minuto Segundo").grid(row=2, column=1, padx=5, pady=5)
ttk.Label(root, text="Nombre del Segmento").grid(row=2, column=2, padx=5, pady=5)

start_time_entries = []
end_time_entries = []
segment_name_entries = []
segment_widgets = []

btn_add_segment = ttk.Button(root, text="Agregar Segmento", command=add_segment_entry)
btn_add_segment.grid(row=4, columnspan=4, pady=10, sticky='ne', padx=(0, 15))

# Fecha personalizada
frame_date = ttk.Frame(root)
frame_date.grid(row=1, column=0, columnspan=5, pady=10, padx=10)

ttk.Label(frame_date, text="Fecha Personalizada (opcional):").grid(row=0, column=0, padx=5)
entry_custom_date = ttk.Entry(frame_date)
entry_custom_date.grid(row=0, column=1, padx=5)
btn_select_date = ttk.Button(frame_date, text="Seleccionar Fecha", command=select_date)
btn_select_date.grid(row=0, column=2, padx=5)

add_segment_entry()

root.mainloop()
