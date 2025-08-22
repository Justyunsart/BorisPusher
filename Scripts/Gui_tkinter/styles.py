from tkinter import ttk


def load_styles(background, text, text_bright)->None:
    """
    EXPECTED TO BE RUN FROM THE ROOT APP OBJECT BEFORE WIDGET INIT!
    Style definitions are offloaded to this script for readability.

    :params:
    All the parameters need to be acceptable inputs for tkinter's color definition (name, hex, etc.)
    """
    style1 = ttk.Style()
    style1.theme_use('default')
    style1.configure('Two.TNotebook.Tab',
                    font=('Arial', 18),
                    padding=8,
                    borderwidth=0,
                    foreground='black',
                    background = text)

    style1.configure('Two.TNotebook',
                    tabposition="n",
                    borderwidth=0,
                    background='white')

    style1.map(
        'Two.TNotebook.Tab',
        background = [("selected", text_bright)],
        foreground = [("selected", 'black')],
        font=[("selected", ('Arial', 18, 'bold'))]
    )

    style = ttk.Style()
    style.theme_use('default')
    style.configure('One.TNotebook.Tab',
                    font=('Arial', 12),
                    padding=(15, 10),
                    justify="center",
                    width=8,
                    borderwidth=0,
                    foreground='light gray',
                    background=background)

    style.configure('One.TNotebook',
                    tabposition='wn',
                    tabmargins=0,
                    borderwidth=0,
                    background=background)
    style.map(
        'One.TNotebook.Tab',
        background=[("selected", background)],
        foreground=[("selected", "white")],
        font=[("selected", ('Arial', 14, 'bold'))]
    )