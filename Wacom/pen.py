import pywinusb.hid as hid
from .constants import *

class Pen:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.pressure = 0
        self.buttons = [False]*BUTTON_QUANTITY
        self.sideButtons = [False]*SIDE_BUTTON_QUANTITY
        self.distance = Distance.OUT

    def update(self, report_id, data):
        if report_id == BUTTONS_REPORT_ID:
            button = data[BUTTON_OFFSET]
            for i in range(BUTTON_QUANTITY):
                self.buttons[i] = (button & (1 << i)) > 0
        elif report_id == BOARD_REPORT_ID:
            distance = data[DISTANCE_OFFSET]

            self.x = data[XCOORD_OFFSET] | (data[XCOORD_OFFSET+1] << BYTE_SIZE) # 2 bytes little-endian
            self.y = data[YCOORD_OFFSET] | (data[YCOORD_OFFSET+1] << BYTE_SIZE)
            self.pressure = data[PRESSURE_OFFSET] | (data[PRESSURE_OFFSET+1] << BYTE_SIZE)

            if distance & 0b00000001:
                self.distance = Distance.TOUCHING
            elif distance == 0b00000000:
                self.distance = Distance.OUT
            elif (distance & 0b01100000) == 0b01100000:
                self.distance = Distance.CLOSE
            elif distance & 0b01000000:
                self.distance = Distance.FAR

            for i in range(SIDE_BUTTON_QUANTITY):
                self.sideButtons[i] = (distance & (1 << i+1)) > 0

    def __str__(self):
        return f"X:{self.x} Y:{self.y} Pressure:{self.pressure} Distance:{self.distance.name} Buttons:{self.buttons} SideButtons:{self.sideButtons}"
    

class WacomTablet:
    def __init__(self, vendor_id=0x056A, product_id=0x0374):
        self.pen = Pen()
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None

    def handler(self, data):
        report_id = data[0]
        self.pen.update(report_id, data)

    def read(self):
        filter = hid.HidDeviceFilter(vendor_id=self.vendor_id, product_id=self.product_id)
        devices = filter.get_devices()

        if devices:
            self.device = devices[0]
            self.device.open()
            self.device.set_raw_data_handler(self.handler)
            return True
        return False
    
    def terminate(self):
        if not self.device: return
        self.device.close()
        self.device = None
