import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import json
import os
import winsound  # Import winsound module for playing sound


class MeetingTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting Timer")
        self.root.geometry("700x450")

        self.mic_icon = tk.PhotoImage(file="MIC.png")  # 加载话筒图标

        # File save path
        self.file_path = "meeting_groups.json"

        # Load or create groups and members
        self.meeting_groups = self.load_groups()

        self.current_group = None
        self.current_person = None
        self.timer_running = False
        self.time_left = 90
        self.timer_finished = False  # Flag to check if timer is finished

        # Sound enabled option
        self.sound_enabled = tk.BooleanVar()
        self.sound_enabled.set(True)  # Enable sound by default

        # Grid layout configuration
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # 1. Meeting notice section (2 rows, 2 columns, bold font)
        info_frame = tk.Frame(root)
        info_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        self.info_label1 = tk.Label(info_frame, text="会议注意事项：", font=("Helvetica", 12, "bold"), fg="red", wraplength=400)
        self.info_label2 = tk.Label(info_frame, text="每人发言保持简洁", font=("Helvetica", 12, "bold"), fg="red", wraplength=400)
        self.info_label3 = tk.Label(info_frame, text="勿打断他人", font=("Helvetica", 12, "bold"), fg="red", wraplength=400)
        self.info_label4 = tk.Label(info_frame, text="可以调整发言时间。", font=("Helvetica", 12, "bold"), fg="red", wraplength=400)

        self.info_label1.grid(row=0, column=0, sticky="w", padx=10)
        self.info_label2.grid(row=0, column=1, sticky="w", padx=10)
        self.info_label3.grid(row=1, column=0, sticky="w", padx=10)
        self.info_label4.grid(row=1, column=1, sticky="w", padx=10)

        # 2. Group selection and operation area
        group_frame = tk.Frame(root)
        group_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        group_label = tk.Label(group_frame, text="Group:")
        group_label.grid(row=0, column=0, padx=10, sticky="w")

        self.group_var = tk.StringVar(root)
        self.group_menu = tk.OptionMenu(group_frame, self.group_var, "")
        self.group_menu.grid(row=0, column=1, padx=10, sticky="w")

        # Add group button
        self.add_group_button = tk.Button(group_frame, text="Add Group", command=self.add_group)
        self.add_group_button.grid(row=0, column=2, padx=10, sticky="w")

        # Delete group button, next to add group button
        self.delete_group_button = tk.Button(group_frame, text="Delete Group", command=self.delete_group)
        self.delete_group_button.grid(row=0, column=3, padx=10, sticky="w")

        # Add person button
        self.add_person_button = tk.Button(group_frame, text="Add Person", command=self.add_person)
        self.add_person_button.grid(row=0, column=4, padx=10, sticky="w")

        # Remove person button
        self.remove_person_button = tk.Button(group_frame, text="Remove Person", command=self.remove_person)
        self.remove_person_button.grid(row=0, column=5, padx=10, sticky="w")

        # 3. Selected person display and countdown area
        display_frame = tk.Frame(root)
        display_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        self.person_label = tk.Label(display_frame, text="No person selected", font=("Helvetica", 18))
        self.person_label.pack()

        self.timer_label = tk.Label(display_frame, text="Countdown: 90s", font=("Helvetica", 24))
        self.timer_label.pack()

        # 4. Time settings and control area
        control_frame = tk.Frame(root)
        control_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

        time_label = tk.Label(control_frame, text="Set time:")
        time_label.pack(side=tk.LEFT, padx=10)

        self.time_entry = tk.Entry(control_frame, width=5)
        self.time_entry.insert(0, "90")
        self.time_entry.pack(side=tk.LEFT, padx=5)

        time_unit_label = tk.Label(control_frame, text="seconds")
        time_unit_label.pack(side=tk.LEFT, padx=5)

        # Randomly choose person button
        self.choose_button = tk.Button(control_frame, text="Choose Random Person", command=self.choose_person)
        self.choose_button.pack(side=tk.LEFT, padx=10)

        # Start timer button
        self.start_button = tk.Button(control_frame, text="Start Timer", command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Reset button
        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset_timer)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        # Sound option checkbox
        self.sound_checkbox = tk.Checkbutton(control_frame, text="Enable Sound", variable=self.sound_enabled)
        self.sound_checkbox.pack(side=tk.LEFT, padx=10)

        # Update menu
        self.update_group_menu()

    def add_group(self):
        group_name = simpledialog.askstring("New Group", "Enter group name:")
        if group_name:
            self.meeting_groups[group_name] = []
            self.update_group_menu()
            self.save_groups()  # Save to file

    def add_person(self):
        if not self.group_var.get():
            messagebox.showwarning("Warning", "Please select a group first")
            return

        person_name = simpledialog.askstring("Add Person", "Enter person's name:")
        if person_name:
            self.meeting_groups[self.group_var.get()].append(person_name)
            self.save_groups()  # Save to file

    def remove_person(self):
        if not self.group_var.get():
            messagebox.showwarning("Warning", "Please select a group first")
            return

        person_name = simpledialog.askstring("Remove Person", "Enter the person's name to remove:")
        if person_name in self.meeting_groups[self.group_var.get()]:
            self.meeting_groups[self.group_var.get()].remove(person_name)
            self.save_groups()  # Save to file
        else:
            messagebox.showwarning("Warning", "This person is not in the current group")

    def delete_group(self):
        """Delete the selected group"""
        group = self.group_var.get()
        if not group:
            messagebox.showwarning("Warning", "Please select a group to delete")
            return
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete group '{group}'? This action cannot be undone.")
        if confirm:
            del self.meeting_groups[group]
            self.update_group_menu()
            self.save_groups()

    def update_group_menu(self):
        self.group_menu['menu'].delete(0, 'end')
        for group in self.meeting_groups.keys():
            self.group_menu['menu'].add_command(label=group, command=tk._setit(self.group_var, group))

    def choose_person(self):
        """Randomly choose a person and display their name"""
        group = self.group_var.get()
        if not group or not self.meeting_groups.get(group):
            messagebox.showwarning("Warning", "Please select a group with members")
            return

        self.current_group = group
        self.current_person = random.choice(self.meeting_groups[group])
        self.person_label.config(text=f"Current Speaker: {self.current_person}")
        self.person_label.config(text=f"Current Speaker: {self.current_person}", image=self.mic_icon, compound='left')

    def start_timer(self):
        """Start the countdown, overriding to show the selected person"""
        if self.timer_running:
            return

        if not self.current_person:
            messagebox.showwarning("Warning", "Please select a random person first")
            return

        self.time_left = int(self.time_entry.get()) if self.time_entry.get().isdigit() else 90
        self.timer_running = True
        self.timer_finished = False
        self.person_label.config(text="")  # Clear selected person and display countdown
        self.countdown()

    def countdown(self):
        if self.time_left > 0:
            self.timer_label.config(text=f"Countdown: {self.time_left}s")
            self.time_left -= 1
            self.root.after(1000, self.countdown)
        else:
            self.timer_label.config(text="Time's up!")
            self.timer_running = False
            self.timer_finished = True
            self.prompt_sound_option()  # Sound option after timer ends

    def reset_timer(self):
        """Reset countdown and update to set time"""
        self.timer_running = False
        self.time_left = int(self.time_entry.get()) if self.time_entry.get().isdigit() else 90
        self.timer_label.config(text=f"Countdown: {self.time_left}s")

    def prompt_sound_option(self):
        """Check if sound is enabled after timer finishes"""
        if self.sound_enabled.get():
            self.play_sound()

    def play_sound(self):
        """Play sound, using Windows system sound"""
        winsound.MessageBeep()  # Play system beep sound

    def save_groups(self):
        """Save groups and members to local file"""
        with open(self.file_path, 'w') as f:
            json.dump(self.meeting_groups, f)

    def load_groups(self):
        """Load groups and members from local file"""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {"Group A": ["Alice", "Bob", "Charlie", "David", "Eve"], "Group B": ["Frank", "Grace", "Hank", "Ivy", "Jack"]}


# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = MeetingTimer(root)
    root.mainloop()
