#!/bin/bash

echo "# install dependent packages.."
sleep 1
apt update && apt install i2c-tools git python3-dev libi2c-dev python3-smbus lm-sensors hdparm python3-psutil -y

echo "# check i2c-dev module.."
sleep 1
MODULE=`cat /etc/modules | grep i2c-dev`
if [ "i2c-dev" != "$MODULE" ];then
  echo "i2c-dev" >> /etc/modules
  modprobe i2c-dev
  echo "# i2c-dev module not enabled.. enabling.."
  echo "# You need to restart ODROID-H2"
  sleep 1
fi

echo "# checking previus installation.."
sleep 1
DIR="/home/odroidlcd/"
if [ -d "$DIR" ]; then
  echo "removing previous installation.."
  rm -rf "$DIR"
fi
echo "# download LCD python code.."
mkdir -p "$DIR"
git clone https://github.com/umbynos/odroidh2_i2c_lcd /home/odroidlcd

echo "# detect i2c ports.."
sleep 1
for BUS in 1 2 3 4 5 6
do
	echo "# i2c port $BUS.."
	if [[ $(i2cdetect -y -r $BUS | grep 27) ]]; then
		echo "# i2c port found: $BUS"
		echo "# edit i2c port number.."
		sleep 1
		sed -i -e "s/BUS = \w/BUS = $BUS/g" /home/odroidlcd/lcddriver.py
	fi
done

echo "# install init.d script.."
sleep 1
cp /home/odroidlcd/odroidlcd.sh /etc/init.d/odroidlcd
chmod a+x /home/odroidlcd/run.sh
chmod a+x /etc/init.d/odroidlcd
update-rc.d odroidlcd defaults

echo "# start oroidlcd service.."
sleep 1
service odroidlcd start

echo "# installation of odroidlcd service finished.."
