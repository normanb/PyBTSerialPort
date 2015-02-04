from pybtserialport import bluetooth as bt

print 'Version: %s' % (bt.__c_api_version__)

inq = bt.DeviceINQ()

print 'Scanning ...'

devices = inq.inquire()

for d in devices:
    print 'Found: %s' % (d.name)
    
    channel_id = inq.search(d.address)
    print 'Channel Id %i' % (channel_id)
    print d.address
 
    port = bt.SerialPortBinding(d.address, channel_id)
    port.connect()


print 'Scanning complete'