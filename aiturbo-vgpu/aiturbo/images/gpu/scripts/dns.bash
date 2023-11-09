filename='/etc/resolv.conf'
cat /dev/null > $filename
echo "nameserver 10.96.0.10" >> $filename
echo "search mzz.svc.cluster.local svc.cluster.local cluster.local" >> $filename
echo "options ndots:5" >> $filename