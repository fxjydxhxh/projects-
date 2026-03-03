import nmap #importar la libreria de nmap 

#i.Inicar el objet ode escaneo 
scanner = nmap.PortScanner()

print("---Escaner de red  hecho en python UwU")
ip = input("Introduce la IP: ")

#2.Ejecuta el escaneo 
#'-v' es para modo verbose(detallado)
#'-sS' es para un escaneo tipo SYN (rapido y silencioso) 
print(f"Escanenado {ip}... ")
scanner.scan(ip, '1-1024','-v -sS')

#3.Procesamos los resultados
#Verificamos si la IP esta encendida 
if ip in scanner.all_hosts():
   print(f"\nEstado del Host: {scanner[ip].state()}")
#Recorremos todos los protoclos encontrados (ej. tcp,udp)
   for proto in scanner[ip].all_protocols():
       print(f"Protocolo: {proto}")

#Obtemos los puertos abiertos para ese protoclo 
       puertos = scanner[ip][proto].keys()

       for port in puertos:
          estado  = scanner[ip][proto][port]['state']
          servicio = scanner[ip][proto][port]['name']
          print(f"Puerto: {port}\tEstado: {estado}\tServicio: {servicio}")
else:
     print("No se encontró el host o esta offline."
)
 
