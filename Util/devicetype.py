# Android = True
# iPhone = False
# iphone_Simulator = False
deviceType = ''
if deviceType == 'Android':
    find_device = 'adb devices'

elif deviceType == 'iPhone':
    find_device = 'idevice_id -l'