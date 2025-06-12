import sys
from PySide6 import QtWidgets
from gui import model, view, controller

def main():
    app = QtWidgets.QApplication(sys.argv)

    my_model = model.MyDLAmodel()

    my_view = view.GridWidget(my_model)  # Pass model into view
    my_controller = controller.DLAController(my_model, my_view)
    my_model.set_start_state(my_controller)


    my_view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
