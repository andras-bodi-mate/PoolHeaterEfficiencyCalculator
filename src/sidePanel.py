import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
from widgets import Slider, RangeSlider, LabeledCheckableComboBox

class SidePanel(qtw.QWidget):
    dateChanged = qtc.pyqtSignal(int)
    requestedCalculation = qtc.pyqtSignal()
    timeIntervalChanged = qtc.pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(200)
        layout = qtw.QVBoxLayout()

        self.dateSlider = Slider("Date", 0, 364, 171)
        self.dateSlider.slider.valueChanged.connect(self.dateChanged.emit)
        self.solarCollectorSelector = LabeledCheckableComboBox("Solar collectors")

        self.exposureTimeIntervalSlider = RangeSlider("Time interval", 0, 24 * 4 - 1)
        self.exposureTimeIntervalSlider.slider.valueChanged.connect(self.timeIntervalChanged)
        self.calculationButton = qtw.QPushButton("Calculate")
        self.calculationButton.pressed.connect(self.requestedCalculation)

        self.powerTable = qtw.QTableWidget(0, 2)
        self.powerTable.setHorizontalHeaderLabels(["Collector", "Power"])
        self.powerTable.verticalHeader().setVisible(False)
        self.powerTable.setEditTriggers(qtw.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.powerTable.setFocusPolicy(qtc.Qt.FocusPolicy.NoFocus)

        self.powerTable.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeMode.Stretch)
        self.powerTable.verticalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeMode.Fixed)

        self.powerTable.setSizePolicy(qtw.QSizePolicy.Policy.Expanding, qtw.QSizePolicy.Policy.Minimum)
        self.powerTable.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.powerTable.setSelectionMode(qtw.QTableWidget.SelectionMode.NoSelection)

        layout.addWidget(self.dateSlider)
        layout.addWidget(self.solarCollectorSelector)
        layout.addWidget(self.exposureTimeIntervalSlider)
        layout.addWidget(self.calculationButton)
        layout.addWidget(self.powerTable)

        layout.addStretch()
        self.setLayout(layout)