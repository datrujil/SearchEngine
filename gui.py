import tkinter as tk
import tkinter.ttk as ttk
import time
import webbrowser

from searchEngine import SearchEngine


def on_hover(event):
    event.widget.configure(foreground="#66ff66", font=("Courier New", 12, "bold"))


def on_leave(event):
    event.widget.configure(foreground="#ffffff", font=("Courier New", 12))


def callback(url):
    webbrowser.open_new(url)


def create_gui():
    search_engine = SearchEngine(index_folder="Indexes")

    results = []
    current_page = 1
    results_per_page = 5
    execution_time_ms = 0 # DT: Store execution time for the current query

    def reset_gui():
        nonlocal output_frame, time_frame, bottom_frame

        # DT: Destroy the previous frames so we can output new search results
        output_frame.destroy()
        time_frame.destroy()

        output_frame = tk.Frame(master=window, bg="#001f00")
        time_frame = tk.Frame(master=window, bg="#001f00")

        for widget in bottom_frame.winfo_children():
            widget.destroy() # DT: Remove the existing buttons

    def display_results():
        reset_gui()

        nonlocal current_page, results

        start_index = (current_page - 1) * results_per_page
        end_index = start_index + results_per_page
        current_results = results[start_index:end_index]

        if current_results:
            for i, (URL, score) in enumerate(current_results, start=start_index + 1): # DT: Enumerating for pagination!
                result_frame = tk.Frame(master=output_frame, bg="#004d00", pady=5, padx=5)
                combined_label = tk.Label(
                    master=result_frame,
                    text=f"{i}. {URL} (Score: {score:.2f})",
                    font=("Courier New", 12),
                    fg="#ffffff",
                    bg="#004d00",
                    cursor="hand2",
                    wraplength=800
                )

                # DT: Bind hover events to underline the URL part
                combined_label.bind("<Button-1>", lambda e, url=URL.strip(): callback(url))
                combined_label.bind("<Enter>", on_hover)
                combined_label.bind("<Leave>", on_leave)
                combined_label.pack(fill=tk.X)

                result_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            no_result_label = tk.Label(
                master=output_frame,
                text="No results found.",
                font=("Courier New", 12),
                fg="#ffffff",
                bg="#001f00",
                anchor="center"
            )
            no_result_label.pack(fill=tk.X, pady=20)

        output_frame.pack(fill=tk.BOTH, expand=True)

        execution = tk.Label(
            master=time_frame,
            text=f"Search Time: {execution_time_ms:.2f} ms",
            font=("Courier New", 10, "italic"),
            fg="#ffffff",
            bg="#001f00"
        )
        execution.pack(fill=tk.X, padx=10)

        # DT: Show Previous and Next buttons
        if current_page > 1:
            prev_button = tk.Button(
                master=bottom_frame,
                text="Previous",
                font=("Courier New", 12),
                fg="#ffffff",
                bg="#004d00",
                activebackground="#006600",
                command=prev_page
            )
            prev_button.pack(side="left", padx=10, pady=10)

        if end_index < len(results): # DT: Check if there are more results to show
            next_button = tk.Button(
                master=bottom_frame,
                text="Next",
                font=("Courier New", 12),
                fg="#ffffff",
                bg="#004d00",
                activebackground="#006600",
                command=next_page
            )
            next_button.pack(side="right", padx=10, pady=10)

        time_frame.pack()

    def handle_search(event=None):
        nonlocal results, current_page, execution_time_ms
        current_page = 1 # DT: Reset to the first page whenever a new search is made
        reset_gui()

        query = search_query.get()
        start_time = time.time()
        results = search_engine.search_query(query)
        execution_time_ms = (time.time() - start_time) * 1000 # DT: Calculate execution time in milliseconds

        display_results()

    def next_page(event=None):
        nonlocal current_page
        if (current_page * results_per_page) < len(results): # DT: Only move to the next page if there are more results
            current_page += 1
            display_results()

    def prev_page(event=None):
        nonlocal current_page
        if current_page > 1:
            current_page -= 1
            display_results()

    def type_title(index=0):
        """Type out the title text one character at a time."""
        if index < len(title_text):
            current_text = title_text[:index + 1]
            header.config(text=current_text)
            window.after(100, type_title, index + 1)

    window = tk.Tk()
    window.title("Real Wide Web")
    window.configure(bg="#001f00")
    window.geometry("1200x800")

    title_text = "Real Wide Web Search Engine"

    header = tk.Label(
        master=window,
        text="Real Wide Web Search Engine",
        font=("Courier New", 24, "bold"),
        fg="#ffffff",
        bg="#001f00",
        anchor="center"
    )
    header.pack(pady=10)

    type_title()

    search_frame = tk.Frame(master=window, bg="#001f00")
    search_query = tk.Entry(
        master=search_frame,
        font=("Courier New", 16),
        fg="#ffffff",
        bg="#004d00",
        insertbackground="#ffffff"
    )
    search_query.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=10, pady=10)
    search_query.bind("<Return>", handle_search)

    search_button = tk.Button(
        master=search_frame,
        text="Search",
        font=("Courier New", 14),
        fg="#00ff00",
        bg="#004d00",
        activebackground="#006600",
        command=handle_search
    )
    search_button.pack(side=tk.RIGHT, padx=10, pady=10)
    search_frame.pack(fill=tk.X)

    output_frame = tk.Frame(master=window, bg="#001f00")
    output_frame.pack(fill=tk.BOTH, expand=True)

    time_frame = tk.Frame(master=window, bg="#001f00")
    bottom_frame = tk.Frame(master=window, bg="#001f00")
    bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)

    # DT: Add keybindings for Shift + < and Shift + >
    window.bind("<Shift-Left>", prev_page)  # DT: Binds Shift + Left Arrow to prev_page
    window.bind("<Shift-Right>", next_page)  # DT: Binds Shift + Right Arrow to next_page

    window.mainloop()


if __name__ == "__main__":
    create_gui()
