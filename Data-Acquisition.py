import pyqtgraph as pg
import pandas as pd
import sys, time

from PySide6.QtSerialPort import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showMaximized()
        self.setWindowTitle('Mach Zehnder Interferometer - DAQ')
        self.init_user_interface()
        self.init_signal_slot()
        self.init_variable()
        self.search_ports()
    
    # Initialize User Interface
    def init_user_interface(self):
        # Connection Group
        self.port_label = QLabel('Port Name')
        self.baud_label = QLabel('Baud Rate')

        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        self.port_combo.lineEdit().setReadOnly(True)
        self.port_combo.lineEdit().setAlignment(Qt.AlignCenter)

        self.baud_combo = QComboBox()
        self.baud_combo.setEditable(True)
        self.baud_combo.lineEdit().setReadOnly(True)
        self.baud_combo.lineEdit().setAlignment(Qt.AlignCenter)
        self.baud_combo.addItems(['9600', '14400', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentIndex(5)

        self.refresh_button = QPushButton('Refresh')
        self.connect_button = QPushButton('Connect')
        self.disconnect_button = QPushButton('Disconnect')
        self.disconnect_button.hide()
        
        self.connection_button = QGridLayout()
        self.connection_button.addWidget(self.port_label, 0, 0)
        self.connection_button.addWidget(self.port_combo, 0, 1)
        self.connection_button.addWidget(self.baud_label, 1, 0)
        self.connection_button.addWidget(self.baud_combo, 1, 1)
        self.connection_button.addWidget(self.refresh_button, 2, 1)
        self.connection_button.addWidget(self.connect_button, 2, 0)
        self.connection_button.addWidget(self.disconnect_button, 2, 0)
        
        self.connection_group = QGroupBox('Connection')
        self.connection_group.setLayout(self.connection_button)

        # File Group
        self.menu = QMenu()
        self.menu.addAction('Amonia', lambda: self.save(0))
        self.menu.addAction('Aseton', lambda: self.save(1))
        self.menu.addAction('Benzena', lambda: self.save(2))
        self.menu.addAction('Etil Asetat', lambda: self.save(3))
        self.menu.addAction('Metana', lambda: self.save(4))
        self.menu.addAction('N-Heksana', lambda: self.save(5))

        self.open_button = QPushButton('Open')
        self.save_button = QPushButton('Save')
        self.save_button.setMenu(self.menu)

        self.file_layout = QGridLayout()
        self.file_layout.addWidget(self.open_button, 0, 0)
        self.file_layout.addWidget(self.save_button, 0, 1)

        self.file_group = QGroupBox('File')
        self.file_group.setLayout(self.file_layout)

        # Control Group
        self.start_button = QPushButton('Start')
        self.stop_button = QPushButton('Stop')
        
        self.control_layout = QGridLayout()
        self.control_layout.addWidget(self.start_button, 0, 0)
        self.control_layout.addWidget(self.stop_button, 0, 1)

        self.control_group = QGroupBox('Control')
        self.control_group.setLayout(self.control_layout)

        # Info Group
        self.sensor_1_label = QLabel('Sensor 1')
        self.sensor_2_label = QLabel('Sensor 2')
        self.sensor_3_label = QLabel('Sensor 3')
        self.humidity_label = QLabel('Humidity')
        self.temperature_label = QLabel('Temperature')

        self.sensor_1_edit = QLineEdit()
        self.sensor_2_edit = QLineEdit()
        self.sensor_3_edit = QLineEdit()
        self.humidity_edit = QLineEdit()
        self.temperature_edit = QLineEdit()

        self.information_layout = QGridLayout()
        self.information_layout.addWidget(self.sensor_1_label, 0, 0)
        self.information_layout.addWidget(self.sensor_1_edit, 0, 1)
        self.information_layout.addWidget(self.sensor_2_label, 1, 0)
        self.information_layout.addWidget(self.sensor_2_edit, 1, 1)
        self.information_layout.addWidget(self.sensor_3_label, 2, 0)
        self.information_layout.addWidget(self.sensor_3_edit, 2, 1)
        self.information_layout.addWidget(self.humidity_label, 3, 0)
        self.information_layout.addWidget(self.humidity_edit, 3, 1)
        self.information_layout.addWidget(self.temperature_label, 4, 0)
        self.information_layout.addWidget(self.temperature_edit, 4, 1)
        self.information_layout.setColumnStretch(0, 1)
        self.information_layout.setColumnStretch(1, 1)

        self.information_group = QGroupBox('Information')
        self.information_group.setLayout(self.information_layout)

        # Left Layout
        self.left_layout = QGridLayout()
        self.left_layout.addWidget(self.connection_group, 0, 0)
        self.left_layout.addWidget(self.file_group, 1, 0)
        self.left_layout.addWidget(self.control_group, 2, 0)
        self.left_layout.addWidget(self.information_group, 3, 0)
        self.left_layout.setRowStretch(4, 1)

        self.left_widget = QWidget()
        self.left_widget.setLayout(self.left_layout)

        # Group Plot
        pg.setConfigOption('foreground', QColor('gray'))
        pg.setConfigOption('background', QColor('transparent'))
        pg.setConfigOption('antialias', True)

        # Plot Sensors
        self.sensor_widget = pg.GraphicsLayoutWidget()
        self.sensor_plot = self.sensor_widget.addPlot(0, 0)

        self.sensor_plot.addLegend(pen='k', labelTextColor='k')
        self.sensor_plot.setMouseEnabled(x=False, y=False)
        self.sensor_plot.hideButtons()

        self.sensor_plot.showAxis('top')
        self.sensor_plot.showAxis('right')

        self.sensor_plot.setLabel('bottom', 'Time')
        self.sensor_plot.setLabel('left', 'Voltage')

        self.sensor_plot.setXRange(0, 3000, padding=0)
        self.sensor_plot.setYRange(0, 1000, padding=0)

        self.sensor_plot.getAxis('top').setZValue(0)
        self.sensor_plot.getAxis('left').setZValue(0)
        self.sensor_plot.getAxis('right').setZValue(0)
        self.sensor_plot.getAxis('bottom').setZValue(0)
        self.sensor_plot.getAxis('top').setStyle(showValues=False)
        self.sensor_plot.getAxis('right').setStyle(showValues=False)

        self.sensor_plot.getViewBox().setBackgroundColor('w')

        self.sensor_1_curve = self.sensor_plot.plot(pen='r', name='Sensor1')
        self.sensor_2_curve = self.sensor_plot.plot(pen='g', name='Sensor2')
        self.sensor_3_curve = self.sensor_plot.plot(pen='b', name='Sensor3')
        
        # Plot Humidity
        self.humidity_widget = pg.GraphicsLayoutWidget()
        self.humidity_plot = self.humidity_widget.addPlot(0, 0)

        self.humidity_plot.addLegend(pen='k', labelTextColor='k')
        self.humidity_plot.setMouseEnabled(x=False, y=False)
        self.humidity_plot.hideButtons()

        self.humidity_plot.showAxis('top')
        self.humidity_plot.showAxis('right')

        self.humidity_plot.setLabel('bottom', 'Time')
        self.humidity_plot.setLabel('left', 'Humidity')

        self.humidity_plot.setXRange(0, 3000, padding=0)
        self.humidity_plot.setYRange(0, 1000, padding=0)

        self.humidity_plot.getAxis('top').setZValue(0)
        self.humidity_plot.getAxis('left').setZValue(0)
        self.humidity_plot.getAxis('right').setZValue(0)
        self.humidity_plot.getAxis('bottom').setZValue(0)
        self.humidity_plot.getAxis('top').setStyle(showValues=False)
        self.humidity_plot.getAxis('right').setStyle(showValues=False)

        self.humidity_plot.getViewBox().setBackgroundColor('w')

        self.humidity_curve = self.humidity_plot.plot(pen='r', name='Humidity')

        # Plot Temperature
        self.temperature_widget = pg.GraphicsLayoutWidget()
        self.temperature_plot = self.temperature_widget.addPlot(0, 0)

        self.temperature_plot.addLegend(pen='k', labelTextColor='k')
        self.temperature_plot.setMouseEnabled(x=False, y=False)
        self.temperature_plot.hideButtons()

        self.temperature_plot.showAxis('top')
        self.temperature_plot.showAxis('right')

        self.temperature_plot.setLabel('bottom', 'Time')
        self.temperature_plot.setLabel('left', 'Temperature')

        self.temperature_plot.setXRange(0, 3000, padding=0)
        self.temperature_plot.setYRange(0, 1000, padding=0)

        self.temperature_plot.getAxis('top').setZValue(0)
        self.temperature_plot.getAxis('left').setZValue(0)
        self.temperature_plot.getAxis('right').setZValue(0)
        self.temperature_plot.getAxis('bottom').setZValue(0)
        self.temperature_plot.getAxis('top').setStyle(showValues=False)
        self.temperature_plot.getAxis('right').setStyle(showValues=False)

        self.temperature_plot.getViewBox().setBackgroundColor('w')

        self.temperature_curve = self.temperature_plot.plot(pen='r', name='Temperature')

        # Right Layout
        self.right_layout = QGridLayout()
        self.right_layout.addWidget(self.sensor_widget, 0, 0)
        self.right_layout.addWidget(self.humidity_widget, 2, 0)
        self.right_layout.addWidget(self.temperature_widget, 1, 0)

        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)

        # Central layout
        self.central_layout = QGridLayout()
        self.central_layout.addWidget(self.left_widget, 0, 0)
        self.central_layout.addWidget(self.right_widget, 0, 1)
        self.central_layout.setColumnStretch(0, 1)
        self.central_layout.setColumnStretch(1, 5)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

        self.serial = QSerialPort()
        self.timer = QTimer()
    
    # Initialize Signals and Slots
    def init_signal_slot(self):
        self.disconnect_button.clicked.connect(self.disconnect)
        self.refresh_button.clicked.connect(self.search_ports)
        self.connect_button.clicked.connect(self.connect)
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        self.open_button.clicked.connect(self.open)
        self.serial.errorOccurred.connect(self.serial_error)
        self.serial.readyRead.connect(self.read_data)

    # Initialize Variables
    def init_variable(self):
        self.dataframe = pd.DataFrame(columns=['Sensor1', 'Sensor2', 'Sensor3', 'Humidity', 'Temperature', 'Gas'])
        self.class_names = ['Amonia', 'Aseton', 'Benzena', 'Etil Asetat', 'Metana', 'N-Heksana']
    
    # Searching for Available Ports
    def search_ports(self):
        self.port_combo.clear()
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.port_combo.addItem(port.systemLocation())
    
    def connect(self):
        self.serial.setPortName(self.port_combo.currentText())
        self.serial.setBaudRate(int(self.baud_combo.currentText()))
        self.serial.open(QIODevice.ReadWrite)
        self.connect_button.hide()
        self.disconnect_button.show()
    
    def disconnect(self):
        self.serial.close()
        self.connect_button.show()
        self.disconnect_button.hide()

    def start(self):
        self.serial.write('M1'.encode())
        self.dataframe = self.dataframe.iloc[0:0]
    
    def stop(self):
        self.serial.write('M3'.encode())

    def save(self, gas_label):
        filename, *_ = QFileDialog.getSaveFileName(self, 'Save File', QDir.currentPath(), 'CSV File (*.csv)')
        self.dataframe['Gas'] = gas_label
        self.dataframe.to_csv(filename)

    def open(self):
        filename, *_ = QFileDialog.getOpenFileName(self, 'Open File', QDir.currentPath(), 'CSV File (*.csv)')
        self.dataframe = pd.read_csv(filename)
        
        self.sensor_1_curve.setData(self.dataframe['Sensor1'].tolist())
        self.sensor_2_curve.setData(self.dataframe['Sensor2'].tolist())
        self.sensor_3_curve.setData(self.dataframe['Sensor3'].tolist())
        self.humidity_curve.setData(self.dataframe['Humidity'].tolist())
        self.temperature_curve.setData(self.dataframe['Temperature'].tolist())
        
    def serial_error(self):
        if self.serial.isOpen():
            self.disconnect()
            self.search_ports()
            print("Not OK")

    def read_data(self):
        while self.serial.canReadLine():
            self.data = self.serial.readLine().trimmed().data()
            if len(self.data) == 29:
                index = len(self.dataframe)
                if index < 3000:
                    self.decodedData = self.data.decode().split()
                    
                    self.dataframe.loc[index, 'Sensor1'] = int(self.decodedData[0])
                    self.dataframe.loc[index, 'Sensor2'] = int(self.decodedData[1])
                    self.dataframe.loc[index, 'Sensor3'] = int(self.decodedData[2])
                    self.dataframe.loc[index, 'Humidity'] = int(self.decodedData[3])
                    self.dataframe.loc[index, 'Temperature'] = int(self.decodedData[4])
                    
                    self.sensor_1_curve.setData(self.dataframe['Sensor1'].tolist())
                    self.sensor_2_curve.setData(self.dataframe['Sensor2'].tolist())
                    self.sensor_3_curve.setData(self.dataframe['Sensor3'].tolist())
                    self.humidity_curve.setData(self.dataframe['Humidity'].tolist())
                    self.temperature_curve.setData(self.dataframe['Temperature'].tolist())
                    
                else:
                    self.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec()
