"""
Converter for network packet capture files (.pcap, .pcapng).
"""

import logging
from pathlib import Path
from typing import Any, Dict

from ..base_converter import BaseConverter

logger = logging.getLogger(__name__)


class PcapConverter(BaseConverter):
    """Converter for PCAP/PCAPNG files."""
    
    def _extract_data(self, file_path: Path, max_packets: int = 10000, **kwargs) -> Dict[str, Any]:
        """
        Extract packets from PCAP file.
        
        Args:
            max_packets: Maximum number of packets to extract (default: 10000)
            
        Returns:
            Dictionary with 'packets' array
        """
        packets = []
        
        # Try pyshark first
        try:
            import pyshark
            return self._extract_with_pyshark(file_path, max_packets)
        except ImportError:
            logger.debug("pyshark not available, trying scapy")
        except Exception as e:
            logger.warning(f"pyshark error: {e}, trying scapy fallback")
        
        # Fallback to scapy
        try:
            from scapy.all import rdpcap, PcapReader
            return self._extract_with_scapy(file_path, max_packets)
        except ImportError:
            raise ImportError(
                "Either pyshark or scapy is required for .pcap files. "
                "Install with: pip install pyshark (requires tshark) or pip install scapy"
            )
    
    def _extract_with_pyshark(self, file_path: Path, max_packets: int) -> Dict[str, Any]:
        """Extract using pyshark."""
        import pyshark
        
        packets = []
        
        try:
            cap = pyshark.FileCapture(
                str(file_path),
                display_filter=None,
                keep_packets=False,  # Don't keep all in memory
            )
            
            for i, packet in enumerate(cap):
                if i >= max_packets:
                    logger.info(f"Reached max_packets limit ({max_packets}), stopping extraction")
                    break
                
                try:
                    packet_obj = {
                        "timestamp": float(packet.sniff_timestamp),
                        "protocol": packet.highest_layer if hasattr(packet, 'highest_layer') else "unknown",
                        "length": int(packet.length) if hasattr(packet, 'length') else 0,
                    }
                    
                    # Extract IP layer info if present
                    if hasattr(packet, 'ip'):
                        packet_obj["src_ip"] = packet.ip.src if hasattr(packet.ip, 'src') else None
                        packet_obj["dst_ip"] = packet.ip.dst if hasattr(packet.ip, 'dst') else None
                        packet_obj["protocol"] = packet.ip.proto if hasattr(packet.ip, 'proto') else None
                    
                    # Extract TCP layer info if present
                    if hasattr(packet, 'tcp'):
                        packet_obj["src_port"] = int(packet.tcp.srcport) if hasattr(packet.tcp, 'srcport') else None
                        packet_obj["dst_port"] = int(packet.tcp.dstport) if hasattr(packet.tcp, 'dstport') else None
                    
                    # Extract UDP layer info if present
                    if hasattr(packet, 'udp'):
                        packet_obj["src_port"] = int(packet.udp.srcport) if hasattr(packet.udp, 'srcport') else None
                        packet_obj["dst_port"] = int(packet.udp.dstport) if hasattr(packet.udp, 'dstport') else None
                    
                    packet_obj["summary"] = str(packet)
                    packets.append(packet_obj)
                    
                except Exception as e:
                    logger.warning(f"Error parsing packet {i}: {e}")
                    continue
            
            cap.close()
            
        except Exception as e:
            logger.error(f"Error reading PCAP file with pyshark {file_path}: {e}")
            raise
        
        return {
            "packet_count": len(packets),
            "packets": packets,
            "extraction_method": "pyshark",
        }
    
    def _extract_with_scapy(self, file_path: Path, max_packets: int) -> Dict[str, Any]:
        """Extract using scapy."""
        from scapy.all import PcapReader
        
        packets = []
        
        try:
            # Use PcapReader for streaming (better for large files)
            reader = PcapReader(str(file_path))
            
            for i, packet in enumerate(reader):
                if i >= max_packets:
                    logger.info(f"Reached max_packets limit ({max_packets}), stopping extraction")
                    break
                
                try:
                    packet_obj = {
                        "timestamp": float(packet.time),
                        "length": len(packet),
                        "summary": packet.summary(),
                    }
                    
                    # Extract IP layer
                    if packet.haslayer("IP"):
                        ip_layer = packet["IP"]
                        packet_obj["src_ip"] = ip_layer.src
                        packet_obj["dst_ip"] = ip_layer.dst
                        packet_obj["protocol"] = ip_layer.proto
                    
                    # Extract TCP layer
                    if packet.haslayer("TCP"):
                        tcp_layer = packet["TCP"]
                        packet_obj["src_port"] = tcp_layer.sport
                        packet_obj["dst_port"] = tcp_layer.dstport
                    
                    # Extract UDP layer
                    if packet.haslayer("UDP"):
                        udp_layer = packet["UDP"]
                        packet_obj["src_port"] = udp_layer.sport
                        packet_obj["dst_port"] = udp_layer.dstport
                    
                    packets.append(packet_obj)
                    
                except Exception as e:
                    logger.warning(f"Error parsing packet {i}: {e}")
                    continue
            
            reader.close()
            
        except Exception as e:
            logger.error(f"Error reading PCAP file with scapy {file_path}: {e}")
            raise
        
        return {
            "packet_count": len(packets),
            "packets": packets,
            "extraction_method": "scapy",
        }

