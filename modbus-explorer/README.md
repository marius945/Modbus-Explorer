# Modbus Explorer

A Home Assistant Add-on for reading and writing Modbus registers with a flexible web interface.

## Features

- **Read registers**: Holding, Input, Coils, Discrete Inputs
- **Write values**: To Holding registers and Coils
- **Multiple data types**: uint16, int16, uint32, int32, float32, uint64, int64, float64
- **Scan function**: Scan a range of registers at once
- **Write test**: Check if a register is writable
- **Dark theme**: Matches Home Assistant's interface
- **Ingress support**: Access directly from HA sidebar

## Installation

### Method 1: Local Add-on Repository

1. Copy the `modbus-explorer` folder to your Home Assistant's `/addons` directory
2. Go to **Settings → Add-ons → Add-on Store**
3. Click the three dots (⋮) in the top right → **Check for updates**
4. The "Modbus Explorer" add-on should appear under "Local add-ons"
5. Click on it and select **Install**

### Method 2: Via Samba/SSH

1. Access your Home Assistant via Samba or SSH
2. Navigate to `/addons/` (create if not exists)
3. Copy the entire `modbus-explorer` folder there
4. Restart Home Assistant
5. Go to Add-on Store and install

## Usage

1. Open Modbus Explorer from the sidebar
2. Enter the IP address of your Modbus device
3. Set the port (default: 502) and Slave ID (default: 1)
4. Choose the register address and type
5. Click **Read Value** to read the current value
6. If writable, enter a new value and click **Write**

### Register Types

| Type | Read | Write | Description |
|------|------|-------|-------------|
| Holding Register | ✓ | ✓ | Read/Write registers (Function codes 3, 6, 16) |
| Input Register | ✓ | ✗ | Read-only registers (Function code 4) |
| Coil | ✓ | ✓ | Read/Write bits (Function codes 1, 5) |
| Discrete Input | ✓ | ✗ | Read-only bits (Function code 2) |

### Data Types

- **uint16**: Unsigned 16-bit integer (0 to 65535)
- **int16**: Signed 16-bit integer (-32768 to 32767)
- **uint32**: Unsigned 32-bit integer (uses 2 registers)
- **int32**: Signed 32-bit integer (uses 2 registers)
- **float32**: 32-bit floating point (uses 2 registers)
- **uint64**: Unsigned 64-bit integer (uses 4 registers)
- **int64**: Signed 64-bit integer (uses 4 registers)
- **float64**: 64-bit floating point (uses 4 registers)

## Configuration

```yaml
default_port: 502        # Default Modbus TCP port
default_slave_id: 1      # Default Modbus slave/unit ID
timeout: 5               # Connection timeout in seconds
```

## Troubleshooting

### Cannot connect to device
- Verify the IP address is correct
- Check that port 502 is not blocked
- Ensure the Modbus device is powered and on the network

### Write operation fails
- The register might be read-only
- Check the device documentation for writable registers
- Verify the Slave ID is correct

### Wrong values displayed
- Check the data type matches the register specification
- Some devices use different byte order (not yet configurable)

## License

MIT License
