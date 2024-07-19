import tkinter as tk
from tkinter import messagebox
from app_ct_reconstruction import image_show
import com_client
import time

start_time = None   # timestamp



def report_execution_time():
    global start_time
    if start_time is None:
        print("No button has been clicked.")
    else:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Total execution time:", elapsed_time, "seconds")
        # process time
        messagebox.showinfo("Execution Time", f"Total execution time: {elapsed_time:.2f} seconds")
        start_time = None


def close_window():
    root.destroy()


def IP_processing():
    global start_time
    messagebox.showinfo("IPv4", "Send service request based on IPv4 packet, start the clock")
    start_time = time.time()
    img_list = com_client.IP_request()
    image_show(img_list)
    report_execution_time()


def IPv6_processing2D():
    global start_time
    messagebox.showinfo("IPv6", "Send service request based on IPv6 packet, start the clock")
    start_time = time.time()
    img_list = com_client.IPv6_request()
    image_show(img_list)
    report_execution_time()


if __name__ == '__main__':

    root = tk.Tk()              
    root.title("ServiceNAT Instance")
    root.geometry("300x200")    # size

    # botton
    ip_button = tk.Button(root, text="IP", command=lambda: IP_processing(), width=10, height=2)
    ip_button.pack(pady=20, padx=50) 

    # botton
    multi_button = tk.Button(root, text="2D_Reconstruction", command=lambda: IPv6_processing2D(), width=20, height=2)
    multi_button.pack(pady=20, padx=50)  

    # close botton
    close_button = tk.Button(root, text="Close", command=close_window)
    close_button.pack()


    root.mainloop()
