import tkinter as tk
import tkinter.ttk as ttk
import time
import webbrowser

from searchEngine import SearchEngine

def on_hover(event):
    event.widget.configure(font=("TkDefaultFont", 13, "underline"))

def on_leave(event):
    event.widget.configure(font=("TkDefaultFont", 13))

def callback(url):
    webbrowser.open_new(url)

def create_gui():

    search_engine = SearchEngine(index_folder="Indexes")

    results = []
    current_page = 1
    results_per_page = 5
    start_time = 0
    execution_time_ms = 0  # DT: Store execution time for the current query

    def reset_gui():
        nonlocal output_frame, time_frame, bottom_frame

        # DT: Destroy the previous frames so we can output new search results
        output_frame.destroy()
        time_frame.destroy()

        output_frame = tk.Frame(
            master=window,
        )

        time_frame = tk.Frame(
            master=window,
            borderwidth=20
        )

        for widget in bottom_frame.winfo_children():
            widget.destroy()  # DT: Remove the existing buttons

    def display_results():
        """Display results for the current page."""
        reset_gui()

        nonlocal current_page, results

        start_index = (current_page - 1) * results_per_page
        end_index = start_index + results_per_page
        current_results = results[start_index:end_index]

        if current_results:
            for i, (URL, score) in enumerate(current_results, start=start_index + 1):   # DT: Enumerating for pagination!
                print(f"URL: {URL}, Score: {score}")  # Debugging purposes

                result_frame = tk.Frame(master=output_frame)
                combined_text = f"{i}. {URL}"
                combined_label = ttk.Label(
                    master=result_frame,
                    text=combined_text,
                    anchor="w"
                )
                combined_label.pack(side="left", padx=5, pady=5)

                # DT: Bind hover events to underline the URL part
                combined_label.bind("<Button-1>", lambda e, url=URL.strip().replace("\xa0", ""): callback(url))
                combined_label.bind("<Enter>", on_hover)
                combined_label.bind("<Leave>", on_leave)

                result_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            no_result_label = ttk.Label(
                master=output_frame,
                text="No results found.",
                anchor="w"
            )
            no_result_label.pack(fill=tk.X, padx=10)

        output_frame.pack(fill=tk.Y, expand=True)

        execution = ttk.Label(
            master=time_frame,
            text=f"Search Time: {execution_time_ms:.2f} milliseconds",
            anchor="w"
        )
        execution.pack(fill=tk.X, padx=10)

        # DT: Show Previous and Next buttons
        if current_page > 1:
            prev_button = ttk.Button(
                master=bottom_frame,
                text="Previous",
                command=prev_page
            )
            prev_button.pack(side="left", padx=10, pady=10)

        if end_index < len(results):  # DT: Check if there are more results to show
            next_button = ttk.Button(
                master=bottom_frame,
                text="Next",
                command=next_page
            )
            next_button.pack(side="right", padx=10, pady=10)

        time_frame.pack()

    def handle_search(event=None):
        nonlocal results, current_page, start_time, execution_time_ms
        current_page = 1  # DT: Reset to the first page whenever a new search is made
        reset_gui()

        start_time = time.time()
        query = search_query.get()

        print("This was your query: ", search_query.get())
        print("You can search through the index here!")
        results = search_engine.search_query(query)
        execution_time_ms = (time.time() - start_time) * 1000  # DT: Calculate execution time in milliseconds

        display_results()

    def next_page(event=None):
        """Move to the next page of results."""
        nonlocal current_page
        if (current_page * results_per_page) < len(results):  # DT: Only move to the next page if there are more results
            current_page += 1
            display_results()

    def prev_page(event=None):
        """Move to the previous page of results."""
        nonlocal current_page
        if current_page > 1:
            current_page -= 1
            display_results()

    window = tk.Tk()
    window.title("Real Wide Web")
    window.attributes("-alpha", 0.98)
    window.minsize(900, 500)

    search_frame = tk.Frame(
        master=window,
        relief=tk.FLAT,
        borderwidth=50
    )
    output_frame = tk.Frame(master=window)
    time_frame = tk.Frame(
        master=window,
        borderwidth=10
    )

    greeting = ttk.Label(
        master=search_frame,
        text="Welcome to the Real Wide Web!"
    )
    greeting.pack()

    search_query = ttk.Entry(

        master=search_frame,
    )
    search_query.pack(fill=tk.X, side=tk.LEFT, expand=True)
    search_query.bind("<Return>", handle_search)

    search_button = ttk.Button(
        master=search_frame,
        text="Search",
        width=10,
        cursor="star",
        command=handle_search
    )
    search_button.pack(side=tk.RIGHT)
    search_frame.pack(fill=tk.X)

    # DT: Button Frame
    bottom_frame = tk.Frame(
        master=window
    )
    bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)

    # DT: Add keybindings for Shift + < and Shift + >
    window.bind("<Shift-Left>", prev_page)  # DT: Binds Shift + Left Arrow to prev_page
    window.bind("<Shift-Right>", next_page)  # DT: Binds Shift + Right Arrow to next_page


    window.mainloop()

if __name__ == "__main__":
    create_gui()