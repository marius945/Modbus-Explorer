#!/usr/bin/env python3
"""Modbus Explorer - Home Assistant Add-on for reading and writing Modbus registers."""

import json
import os
import struct
from flask import Flask, render_template, request, jsonify
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

app = Flask(__name__)

# Load options from Home Assistant
OPTIONS_PATH = "/data/options.json"
if os.path.exists(OPTIONS_PATH):
    with open(OPTIONS_PATH, "r") as f:
        OPTIONS = json.load(f)
else:
    OPTIONS = {
        "default_port": 502,
        "default_slave_id": 1,
        "timeout": 5
    }

# Data type configurations
DATA_TYPES = {
    "uint16": {"size": 1, "pack": ">H", "min": 0, "max": 65535},
    "int16": {"size": 1, "pack": ">h", "min": -32768, "max": 32767},
    "uint32": {"size": 2, "pack": ">I", "min": 0, "max": 4294967295},
    "int32": {"size": 2, "pack": ">i", "min": -2147483648, "max": 2147483647},
    "float32": {"size": 2, "pack": ">f", "min": None, "max": None},
    "uint64": {"size": 4, "pack": ">Q", "min": 0, "max": 18446744073709551615},
    "int64": {"size": 4, "pack": ">q", "min": None, "max": None},
    "float64": {"size": 4, "pack": ">d", "min": None, "max": None},
}


def decode_registers(registers, data_type):
    """Decode Modbus registers to the specified data type."""
    if data_type not in DATA_TYPES:
        return None, f"Unknown data type: {data_type}"

    config = DATA_TYPES[data_type]
    if len(registers) < config["size"]:
        return None, f"Not enough registers for {data_type}"

    # Convert registers to bytes (big-endian)
    byte_data = b""
    for reg in registers[:config["size"]]:
        byte_data += struct.pack(">H", reg)

    # Unpack to the target type
    try:
        value = struct.unpack(config["pack"], byte_data)[0]
        return value, None
    except struct.error as e:
        return None, str(e)


def encode_value(value, data_type):
    """Encode a value to Modbus registers."""
    if data_type not in DATA_TYPES:
        return None, f"Unknown data type: {data_type}"

    config = DATA_TYPES[data_type]

    try:
        # Convert string value to appropriate type
        if "float" in data_type:
            value = float(value)
        else:
            value = int(value)

        # Pack value to bytes
        byte_data = struct.pack(config["pack"], value)

        # Convert bytes to registers
        registers = []
        for i in range(0, len(byte_data), 2):
            reg = struct.unpack(">H", byte_data[i:i+2])[0]
            registers.append(reg)

        return registers, None
    except (ValueError, struct.error) as e:
        return None, str(e)


@app.route("/")
def index():
    """Render the main page."""
    return render_template(
        "index.html",
        default_port=OPTIONS["default_port"],
        default_slave_id=OPTIONS["default_slave_id"],
        data_types=list(DATA_TYPES.keys())
    )


@app.route("/api/read", methods=["POST"])
def read_register():
    """Read a Modbus register."""
    data = request.json

    ip = data.get("ip", "").strip()
    port = int(data.get("port", OPTIONS["default_port"]))
    slave_id = int(data.get("slave_id", OPTIONS["default_slave_id"]))
    address = int(data.get("address", 0))
    data_type = data.get("data_type", "uint16")
    register_type = data.get("register_type", "holding")

    if not ip:
        return jsonify({"success": False, "error": "IP address is required"})

    client = ModbusTcpClient(ip, port=port, timeout=OPTIONS["timeout"])

    try:
        if not client.connect():
            return jsonify({"success": False, "error": f"Could not connect to {ip}:{port}"})

        count = DATA_TYPES.get(data_type, {}).get("size", 1)

        # Read registers based on type
        if register_type == "holding":
            result = client.read_holding_registers(address, count=count, slave=slave_id)
        elif register_type == "input":
            result = client.read_input_registers(address, count=count, slave=slave_id)
        elif register_type == "coil":
            result = client.read_coils(address, count=1, slave=slave_id)
            if not result.isError():
                return jsonify({
                    "success": True,
                    "value": 1 if result.bits[0] else 0,
                    "raw": [1 if result.bits[0] else 0],
                    "writable": True
                })
        elif register_type == "discrete":
            result = client.read_discrete_inputs(address, count=1, slave=slave_id)
            if not result.isError():
                return jsonify({
                    "success": True,
                    "value": 1 if result.bits[0] else 0,
                    "raw": [1 if result.bits[0] else 0],
                    "writable": False  # Discrete inputs are read-only
                })
        else:
            return jsonify({"success": False, "error": f"Unknown register type: {register_type}"})

        if result.isError():
            return jsonify({"success": False, "error": str(result)})

        value, error = decode_registers(result.registers, data_type)
        if error:
            return jsonify({"success": False, "error": error})

        # Determine if writable (holding registers and coils are writable)
        writable = register_type in ["holding", "coil"]

        return jsonify({
            "success": True,
            "value": value,
            "raw": list(result.registers),
            "writable": writable
        })

    except ModbusException as e:
        return jsonify({"success": False, "error": f"Modbus error: {str(e)}"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"})
    finally:
        client.close()


@app.route("/api/write", methods=["POST"])
def write_register():
    """Write a value to a Modbus register."""
    data = request.json

    ip = data.get("ip", "").strip()
    port = int(data.get("port", OPTIONS["default_port"]))
    slave_id = int(data.get("slave_id", OPTIONS["default_slave_id"]))
    address = int(data.get("address", 0))
    value = data.get("value")
    data_type = data.get("data_type", "uint16")
    register_type = data.get("register_type", "holding")

    if not ip:
        return jsonify({"success": False, "error": "IP address is required"})

    if value is None or value == "":
        return jsonify({"success": False, "error": "Value is required"})

    # Check if register type is writable
    if register_type not in ["holding", "coil"]:
        return jsonify({"success": False, "error": f"Register type '{register_type}' is read-only"})

    client = ModbusTcpClient(ip, port=port, timeout=OPTIONS["timeout"])

    try:
        if not client.connect():
            return jsonify({"success": False, "error": f"Could not connect to {ip}:{port}"})

        if register_type == "coil":
            # Write coil (boolean)
            coil_value = bool(int(value))
            result = client.write_coil(address, coil_value, slave=slave_id)
        else:
            # Encode value to registers
            registers, error = encode_value(value, data_type)
            if error:
                return jsonify({"success": False, "error": f"Encoding error: {error}"})

            # Write registers
            if len(registers) == 1:
                result = client.write_register(address, registers[0], slave=slave_id)
            else:
                result = client.write_registers(address, registers, slave=slave_id)

        if result.isError():
            return jsonify({
                "success": False,
                "error": f"Write failed: {str(result)} - Register may be read-only"
            })

        return jsonify({"success": True, "message": "Value written successfully"})

    except ModbusException as e:
        return jsonify({"success": False, "error": f"Modbus error: {str(e)}"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"})
    finally:
        client.close()


@app.route("/api/scan", methods=["POST"])
def scan_registers():
    """Scan a range of registers."""
    data = request.json

    ip = data.get("ip", "").strip()
    port = int(data.get("port", OPTIONS["default_port"]))
    slave_id = int(data.get("slave_id", OPTIONS["default_slave_id"]))
    start_address = int(data.get("start_address", 0))
    end_address = int(data.get("end_address", 10))
    data_type = data.get("data_type", "uint16")
    register_type = data.get("register_type", "holding")

    if not ip:
        return jsonify({"success": False, "error": "IP address is required"})

    if end_address < start_address:
        return jsonify({"success": False, "error": "End address must be >= start address"})

    if end_address - start_address > 100:
        return jsonify({"success": False, "error": "Maximum scan range is 100 registers"})

    client = ModbusTcpClient(ip, port=port, timeout=OPTIONS["timeout"])
    results = []

    try:
        if not client.connect():
            return jsonify({"success": False, "error": f"Could not connect to {ip}:{port}"})

        reg_size = DATA_TYPES.get(data_type, {}).get("size", 1)

        for addr in range(start_address, end_address + 1, reg_size):
            try:
                if register_type == "holding":
                    result = client.read_holding_registers(addr, count=reg_size, slave=slave_id)
                elif register_type == "input":
                    result = client.read_input_registers(addr, count=reg_size, slave=slave_id)
                elif register_type == "coil":
                    result = client.read_coils(addr, count=1, slave=slave_id)
                    if not result.isError():
                        results.append({
                            "address": addr,
                            "value": 1 if result.bits[0] else 0,
                            "raw": [1 if result.bits[0] else 0],
                            "error": None
                        })
                    else:
                        results.append({
                            "address": addr,
                            "value": None,
                            "raw": None,
                            "error": str(result)
                        })
                    continue
                elif register_type == "discrete":
                    result = client.read_discrete_inputs(addr, count=1, slave=slave_id)
                    if not result.isError():
                        results.append({
                            "address": addr,
                            "value": 1 if result.bits[0] else 0,
                            "raw": [1 if result.bits[0] else 0],
                            "error": None
                        })
                    else:
                        results.append({
                            "address": addr,
                            "value": None,
                            "raw": None,
                            "error": str(result)
                        })
                    continue

                if result.isError():
                    results.append({
                        "address": addr,
                        "value": None,
                        "raw": None,
                        "error": str(result)
                    })
                else:
                    value, error = decode_registers(result.registers, data_type)
                    results.append({
                        "address": addr,
                        "value": value,
                        "raw": list(result.registers),
                        "error": error
                    })
            except Exception as e:
                results.append({
                    "address": addr,
                    "value": None,
                    "raw": None,
                    "error": str(e)
                })

        return jsonify({"success": True, "results": results})

    except ModbusException as e:
        return jsonify({"success": False, "error": f"Modbus error: {str(e)}"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"})
    finally:
        client.close()


@app.route("/api/test_write", methods=["POST"])
def test_write():
    """Test if a register is writable by attempting to write its current value."""
    data = request.json

    ip = data.get("ip", "").strip()
    port = int(data.get("port", OPTIONS["default_port"]))
    slave_id = int(data.get("slave_id", OPTIONS["default_slave_id"]))
    address = int(data.get("address", 0))
    register_type = data.get("register_type", "holding")

    if not ip:
        return jsonify({"success": False, "error": "IP address is required"})

    # Only holding registers and coils can be writable
    if register_type not in ["holding", "coil"]:
        return jsonify({
            "success": True,
            "writable": False,
            "reason": f"Register type '{register_type}' is always read-only by Modbus specification"
        })

    client = ModbusTcpClient(ip, port=port, timeout=OPTIONS["timeout"])

    try:
        if not client.connect():
            return jsonify({"success": False, "error": f"Could not connect to {ip}:{port}"})

        if register_type == "coil":
            # Read current value
            read_result = client.read_coils(address, count=1, slave=slave_id)
            if read_result.isError():
                return jsonify({"success": False, "error": f"Could not read coil: {str(read_result)}"})

            current_value = read_result.bits[0]

            # Try to write the same value back
            write_result = client.write_coil(address, current_value, slave=slave_id)

        else:  # holding register
            # Read current value
            read_result = client.read_holding_registers(address, count=1, slave=slave_id)
            if read_result.isError():
                return jsonify({"success": False, "error": f"Could not read register: {str(read_result)}"})

            current_value = read_result.registers[0]

            # Try to write the same value back
            write_result = client.write_register(address, current_value, slave=slave_id)

        if write_result.isError():
            return jsonify({
                "success": True,
                "writable": False,
                "reason": f"Write test failed: {str(write_result)}"
            })

        return jsonify({
            "success": True,
            "writable": True,
            "reason": "Register accepted write operation"
        })

    except ModbusException as e:
        return jsonify({"success": False, "error": f"Modbus error: {str(e)}"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"})
    finally:
        client.close()


if __name__ == "__main__":
    # Get ingress path from environment
    ingress_path = os.environ.get("INGRESS_PATH", "")

    app.run(host="0.0.0.0", port=5000, debug=False)
