# Lab 3 Skeleton
#
# Based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Firewall (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

  def do_firewall (self, packet, packet_in):
    # The code in here will be executed for every packet.
    #print "Example Code."

    def flood():
      # 1) send the original message 
      #of.ofp_packet_out(in_port=of.0FPP_NONE)

      # 2) send message to controller
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      self.connection.send(msg)

    def drop():
      # 1) send message to controller
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.idle_timeout = 30 #gets deleted after time if rule no applied
      msg.hard_timeout = 30 #gets deleted no matter what after time
      msg.buffer_id = packet_in.buffer_id
      self.connection.send(msg)

    if packet.find('ipv4'): # if IPV4
      if packet.find('tcp'): # TCP
        flood()
      else: # UDP (is IPV4 but not TCP)
        drop()
    elif packet.find('arp'): # ARP
      flood()
    else: # ICMP
      drop()
      
      

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_firewall(packet, packet_in)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Firewall(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
