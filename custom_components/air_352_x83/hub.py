import asyncio
import socket
import logging
from datetime import datetime
from .const import UDP_PORT, COMMANDS

_LOGGER = logging.getLogger(__name__)

class X83Hub:
    def __init__(self, hass, host, mac, model):
        self.hass = hass
        self.host = host
        self.mac = mac.replace(":", "").upper()
        self.model = model
        self.current_seq = 0
        self.last_seen = 0
        self.command_lock = 0
        self.status = {
            "pm25": 0, "speed": 0, "power": "OFF", "light": True, "mode": "None",
            "filter_installed": "未安装", "total_purification": 0, "online": False
        }
        self._callbacks = set()

    def register_callback(self, callback):
        self._callbacks.add(callback)

    def remove_callback(self, callback):
        self._callbacks.discard(callback)

    def _assemble(self, seq, hex_payload):
        dev_type = "03" if self.model == "x50" else "02"
        header = bytes.fromhex(f"A104{self.mac}0E00")
        seq_bytes = seq.to_bytes(2, 'big')
        body = bytes.fromhex(f"F1{dev_type}050401A5A0{hex_payload}0000")
        return header + seq_bytes + body

    async def async_control(self, action):
        now = datetime.now().timestamp()
        self.command_lock = now + 3.0 
        
        if (now - self.last_seen) > 20:
            await self._async_wakeup()
            await asyncio.sleep(0.5)

        hex_code = COMMANDS.get(action, "0000")
        packet = self._assemble(self.current_seq + 1, hex_code)
        await self._async_send(packet)

    async def _async_wakeup(self):
        discovery = bytes.fromhex(f"A104{self.mac}08000000F102050423")
        await self._async_send(discovery, broadcast=True)

    async def _async_send(self, packet, broadcast=False):
        def _send():
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                if broadcast:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    s.sendto(packet, ("255.255.255.255", UDP_PORT))
                else:
                    s.sendto(packet, (self.host, UDP_PORT))
        await asyncio.get_running_loop().run_in_executor(None, _send)

    def parse_data(self, data):
        if len(data) < 30 or data[0] != 0xA1: return
        
        self.current_seq = int.from_bytes(data[10:12], 'big')
        now = datetime.now().timestamp()
        self.last_seen = now
        
        if data[13] == 2:
            self.model = "x83"
            base = 16
        elif data[13] == 3:
            self.model = "x50"
            base = 24
        else:
            base = 16
            
        try:
            power = "ON" if data[base + 9] == 0x00 else "OFF"
            speed = data[base + 4]
            val_b3 = data[base + 3]
            mode_map = {1: "auto", 2: "sleep", 3: "turbo", 5: "manual"}
            mode = mode_map.get(val_b3 & 0x0F, "None")
            
            is_locked = now < self.command_lock
            
            if not is_locked:
                self.status["power"] = power
                self.status["speed"] = speed
                self.status["mode"] = mode
            
            self.status["pm25"] = (data[base + 12] << 8) | data[base + 13]
            self.status["light"] = True if data[base + 8] == 0x00 else False
            
            filter_type = (val_b3 & 0xF0) >> 4
            self.status["filter_installed"] = "已安装" if filter_type in [1, 2] else "未安装"
                
            pur_base = (data[base + 25] << 8) | data[base + 26]
            m_idx_pur = data[base + 24] if data[base + 24] < 4 else 0
            purification = pur_base * (10 ** m_idx_pur)
            if purification < 9999999:
                self.status["total_purification"] = purification
                
            self.status["online"] = True
        except Exception:
            pass

        for callback in self._callbacks:
            callback()