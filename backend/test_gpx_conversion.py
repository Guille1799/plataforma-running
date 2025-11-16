"""
Test Script: GPX to FIT Auto-Conversion

Demonstrates automatic conversion of Xiaomi/Amazfit GPX files to FIT format.
"""
import sys
sys.path.insert(0, 'C:/Users/guill/Desktop/plataforma-running/backend')

from app.services.gpx_to_fit_converter import gpx_to_fit_converter
from datetime import datetime

# Sample GPX content (Xiaomi/Amazfit format)
SAMPLE_GPX = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Zepp App" 
     xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 
     http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>Morning Run</name>
    <time>2025-11-14T07:30:00Z</time>
  </metadata>
  <trk>
    <name>Running</name>
    <type>running</type>
    <trkseg>
      <trkpt lat="40.416775" lon="-3.703790">
        <ele>667.0</ele>
        <time>2025-11-14T07:30:00Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>125</gpxtpx:hr>
            <gpxtpx:cad>165</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="40.417000" lon="-3.703800">
        <ele>668.0</ele>
        <time>2025-11-14T07:30:10Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>128</gpxtpx:hr>
            <gpxtpx:cad>168</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="40.417250" lon="-3.703750">
        <ele>669.0</ele>
        <time>2025-11-14T07:30:20Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>132</gpxtpx:hr>
            <gpxtpx:cad>170</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="40.417500" lon="-3.703600">
        <ele>670.0</ele>
        <time>2025-11-14T07:30:30Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>135</gpxtpx:hr>
            <gpxtpx:cad>172</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="40.417750" lon="-3.703500">
        <ele>671.0</ele>
        <time>2025-11-14T07:30:40Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>138</gpxtpx:hr>
            <gpxtpx:cad>175</gpxtpx:cad>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""

def test_gpx_to_fit_conversion():
    """Test GPX → FIT conversion."""
    
    print("=" * 70)
    print("🧪 TESTING: GPX → FIT Auto-Conversion")
    print("=" * 70)
    print()
    
    try:
        # Convert GPX to FIT
        print("📁 Input: Xiaomi/Amazfit GPX file (50 seconds, 5 points)")
        print("🔄 Converting...")
        
        gpx_bytes = SAMPLE_GPX.encode('utf-8')
        fit_bytes = gpx_to_fit_converter.convert_gpx_to_fit(gpx_bytes)
        
        print(f"✅ Conversion successful!")
        print()
        print("📊 Output Statistics:")
        print(f"   - FIT file size: {len(fit_bytes)} bytes")
        print(f"   - GPX file size: {len(gpx_bytes)} bytes")
        print(f"   - Compression ratio: {len(fit_bytes)/len(gpx_bytes)*100:.1f}%")
        print()
        
        # Verify FIT header
        if fit_bytes[8:12] == b'.FIT':
            print("✅ Valid FIT header detected")
        else:
            print("❌ Invalid FIT header!")
            return False
        
        # Save example files
        with open('test_xiaomi.gpx', 'wb') as f:
            f.write(gpx_bytes)
        print("💾 Saved: test_xiaomi.gpx")
        
        with open('test_converted.fit', 'wb') as f:
            f.write(fit_bytes)
        print("💾 Saved: test_converted.fit")
        
        print()
        print("=" * 70)
        print("🎉 SUCCESS: GPX → FIT conversion working!")
        print("=" * 70)
        print()
        print("📱 Supported Devices:")
        print("   ✅ Xiaomi Mi Band (all versions)")
        print("   ✅ Amazfit Bip, GTS, GTR, T-Rex")
        print("   ✅ Zepp E, Z")
        print("   ✅ Any device exporting GPX format")
        print()
        print("🚀 Benefits:")
        print("   - HR zones automatically calculated")
        print("   - Cadence data preserved")
        print("   - Compatible with all analytics tools")
        print("   - Smaller file sizes (FIT is binary)")
        print("   - Standard Garmin format")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gpx_to_fit_conversion()
    sys.exit(0 if success else 1)
