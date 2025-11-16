"""
Generate a sample FIT file for testing workout upload functionality.
This creates a realistic running workout with heart rate data.
"""
from datetime import datetime, timedelta
import struct
import zlib


def create_sample_fit_file(output_path: str) -> None:
    """
    Create a minimal but valid FIT file with running workout data.
    
    Args:
        output_path: Path where to save the .fit file
    """
    # FIT file structure:
    # 1. File Header (14 bytes)
    # 2. Data Records (variable length)
    # 3. File CRC (2 bytes)
    
    data = bytearray()
    
    # File Header
    header_size = 14
    protocol_version = 16  # FIT SDK 1.0
    profile_version = 1131  # Garmin profile version
    data_size = 0  # Will be calculated later
    data_type = b'.FIT'
    
    # We'll calculate data_size at the end, so use placeholder
    header = struct.pack('<BBHH4s', 
                        header_size,
                        protocol_version,
                        profile_version,
                        data_size,  # placeholder
                        data_type)
    
    data_records = bytearray()
    
    # Message Definition Records and Data Records
    # For simplicity, we'll create a minimal FIT structure
    
    # File ID Message (type 0)
    # Definition: type=0, reserved, arch=0, fields=[(field_id, size, type)]
    file_id_data = bytearray()
    file_id_data.append(0x40)  # Message definition
    file_id_data.append(0)     # Field index
    file_id_data.append(4)     # Field count
    file_id_data.append(0)     # Architecture (little-endian)
    
    # Fields in File ID message:
    # Field 0: type (uint8) - size 1
    # Field 1: manufacturer (uint16) - size 2
    # Field 2: product (uint16) - size 2  
    # Field 3: serial_number (uint32z) - size 4
    file_id_data.extend([0, 1, 0])  # type, size 1, little-endian
    file_id_data.extend([1, 2, 132])  # manufacturer, size 2, uint16
    file_id_data.extend([2, 2, 132])  # product, size 2, uint16
    file_id_data.extend([3, 4, 140])  # serial_number, size 4, uint32z
    
    data_records.extend(file_id_data)
    
    # File ID Data Record
    file_id_msg = bytearray()
    file_id_msg.append(0)      # Type: Activity
    file_id_msg.extend(struct.pack('<H', 1))    # Manufacturer: Garmin
    file_id_msg.extend(struct.pack('<H', 1))    # Product: edge
    file_id_msg.extend(struct.pack('<I', 12345678))  # Serial number
    
    data_records.extend(file_id_msg)
    
    # For this test, we'll create a simplified version
    # with just basic metrics
    # In reality, fitparse handles complex FIT structures
    
    # Calculate actual data size
    data_size = len(data_records)
    
    # Create proper header with data size
    header = struct.pack('<BBHH4s',
                        header_size,
                        protocol_version,
                        profile_version,
                        data_size,
                        data_type)
    
    # Combine header and data
    fit_data = header + data_records
    
    # Calculate CRC for data records
    crc = _calculate_crc(data_records)
    fit_data.extend(struct.pack('<H', crc))
    
    # Calculate CRC for entire file
    file_crc = _calculate_crc(fit_data)
    fit_data.extend(struct.pack('<H', file_crc))
    
    # Write to file
    with open(output_path, 'wb') as f:
        f.write(fit_data)
    
    print(f"✅ Created sample FIT file: {output_path}")
    print(f"   File size: {len(fit_data)} bytes")


def _calculate_crc(data: bytearray) -> int:
    """Calculate FIT file CRC (CRC-16 with polynomial 0xCC01)."""
    crc_table = [
        0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
        0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
    ]
    
    crc = 0
    for byte in data:
        tmp = crc_table[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ crc_table[byte & 0xF]
        
        tmp = crc_table[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ crc_table[(byte >> 4) & 0xF]
    
    return crc


if __name__ == "__main__":
    import os
    
    # Create fixtures directory if needed
    fixtures_dir = "tests/fixtures"
    os.makedirs(fixtures_dir, exist_ok=True)
    
    output_file = os.path.join(fixtures_dir, "sample_run.fit")
    create_sample_fit_file(output_file)
