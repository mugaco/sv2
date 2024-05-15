# import itertools
# import time
# import sys
# import threading


# def start_spinner():
#     spinner_symbols = itertools.cycle(["-", "/", "|", "\\"])
#     running = True

#     def spinner():
#         while running:
#             sys.stdout.write(
#                 next(spinner_symbols)
#             )  # Muestra el símbolo actual del spinner
#             sys.stdout.flush()
#             time.sleep(0.1)  # Controla la velocidad del spinner
#             # sys.stdout.write("\b")  # Regresa el cursor para sobrescribir el símbolo
#             sys.stdout.write("\b \b")
#             sys.stdout.flush()
#     spinner_thread = threading.Thread(target=spinner)
#     spinner_thread.start()

#     def stop():
#         nonlocal running
#         running = False
#         spinner_thread.join()

#     return stop
import itertools
import time
import sys
import threading


def start_spinner():
    spinner_symbols = itertools.cycle(["-", "/", "|", "\\"])
    running = True
    cleaned = False  # Añadimos una bandera para controlar la limpieza final

    def spinner():
        while running:
            sys.stdout.write(
                next(spinner_symbols)
            )  # Muestra el símbolo actual del spinner
            sys.stdout.flush()
            time.sleep(0.1)  # Controla la velocidad del spinner
            sys.stdout.write("\b")  # Regresa el cursor para sobrescribir el símbolo
        if not cleaned:  # Si aún no se ha limpiado después de detener
            sys.stdout.write(" \b")  # Borramos el último símbolo visiblemente
            sys.stdout.flush()

    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()

    def stop():
        nonlocal running, cleaned
        running = False
        spinner_thread.join()  # Espera a que el hilo del spinner termine
        cleaned = True
        sys.stdout.write(" \b")  # Asegúrate de borrar el último símbolo
        sys.stdout.flush()

    return stop
