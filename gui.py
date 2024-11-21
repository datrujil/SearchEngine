import tkinter as tk
import tkinter.ttk as ttk
import time

def create_gui():
    def handle_search():
        # Allow modification of the outer variables
        nonlocal output_frame, time_frame

        # Destroy the previous frames so we can output new search results
        output_frame.destroy()
        time_frame.destroy()

        # Recreate new frames
        output_frame = tk.Frame(master=window)
        time_frame = tk.Frame(master=window)

        # Time the search
        start_time = time.time()

        # TODO: ** This is where you can obtain the query for searching **
        print("This was your query: ", search_query.get())
        print("You can search through the index here!")

        # You're going to want to get the top results and create labels to the output_frame
        # Here's an example, we'll need to do this for the top 5 URLs obtained from the search
        URL = "www.example.com"
        result_example = ttk.Label(
                master=output_frame,
                text=f"{URL}\n"
        )
        result_example.pack()
        output_frame.pack(fill=tk.Y, expand=True)

        execution = ttk.Label(
            master=time_frame,
            text=f"Search Time: {time.time() - start_time} seconds"
        )
        execution.pack()
        time_frame.pack()


    # Initialize all frames
    window = tk.Tk()
    search_frame = tk.Frame(
        master=window,
        relief=tk.FLAT,
        borderwidth=50
    )
    output_frame = tk.Frame(master=window)
    time_frame = tk.Frame(master=window)

    # Create GUI components
    greeting = ttk.Label(
        master=search_frame,
        text="Welcome to the Real Wide Web!"
    )
    greeting.pack()

    search_query = ttk.Entry(
        master=search_frame,
    )
    search_query.pack(fill=tk.X, side=tk.LEFT, expand=True)

    search_button = ttk.Button(
        master=search_frame,
        text="Search",
        width=10,
        command=handle_search
    )
    search_button.pack(side=tk.RIGHT)
    search_button.bind("<Button-1>", )

    search_frame.pack(fill=tk.X)

    window.mainloop()

if __name__ == "__main__":
    create_gui()