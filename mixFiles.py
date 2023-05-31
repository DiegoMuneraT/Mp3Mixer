import multiprocessing
import time
from pydub import AudioSegment

#-------------------------------------------------------------------------------------------
def mix_en_paralelo(archivo1, archivo2, salida):

    print("|-> En paralelo <-|")

    # Iniciamos el tiempo de ejecucion
    tiempo_in = time.time()

    # Primero cargamos los archivos
    audio1 = AudioSegment.from_mp3(archivo1)
    audio2 = AudioSegment.from_mp3(archivo2)

    # Nos aseguramos que ambos archivos tengan la misma longitud
    max_length = max(len(audio1), len(audio2))
    if len(audio1) < max_length:
        audio1 += AudioSegment.silent(duration=max_length - len(audio1))
        audio2 = audio2[:max_length]
    elif len(audio2) < max_length:
        audio2 += AudioSegment.silent(duration=max_length - len(audio2))
        audio1 = audio1[:max_length]

    # Partimos los audios
    audio1_part1 = audio1[:len(audio1)//2]
    audio1_part2 = audio1[len(audio1)//2:]

    audio2_part1 = audio2[:len(audio2)//2]
    audio2_part2 = audio2[len(audio2)//2:]

    #Creamos un Pool de procesamiento
    pool = multiprocessing.Pool(processes=8)

    # Mixeamos la primera parte en paralelo
    primera_parte = pool.starmap(sobreponer_segmentos, [(audio1_part1, audio2_part1)])

    # Mixeamos la segunda parte en paralelo
    segunda_parte = pool.starmap(sobreponer_segmentos, [(audio1_part2, audio2_part2)])

    # Unimos las partes
    list = primera_parte + segunda_parte

    # Aplicamos la formula y sumamos los segmentos con G = 0.00005
    combined = AudioSegment.empty()
    for segment in list:
        combined += segment.apply_gain(0.00005 * segment.max_possible_amplitude)

    # Exportamos en el archivo de salida
    combined.export(f"./{salida}_paralelo.mp3", format="mp3")

    # Detenemos el tiempo de ejecucion
    tiempo_out = time.time()

    print(f'Tiempo de ejecucion: {tiempo_out-tiempo_in}')

#-------------------------------------------------------------------------------------------
def mix_en_secuencial(archivo1, archivo2, salida):

    print("|-> En secuencial <-|")

    #Iniciamos el tiempo de ejecucion
    tiempo_in = time.time()

    #Primero cargamos los archivos
    audio1 = AudioSegment.from_file(archivo1, format="mp3")
    audio2 = AudioSegment.from_file(archivo2, format="mp3")

    #Luego los seteamos al que dure mas
    max_length = max(len(audio1), len(audio2))
    if len(audio1) < max_length:
        audio1 += AudioSegment.silent(duration=max_length - len(audio1))
        audio2 = audio2[:max_length]
    elif len(audio2) < max_length:
        audio2 += AudioSegment.silent(duration=max_length - len(audio2))
        audio1 = audio1[:max_length]

    #Mixemos secuencialmente
    mix_secuencial = sobreponer_segmentos(audio1[:max_length], audio2[:max_length])

    #Exportamos en el archivo de salida
    mix_secuencial.export(f"{salida}_secuencial.mp3", format="mp3")

    #Detenemos el tiempo de ejecucion
    tiempo_out = time.time()

    print(f'Tiempo de ejecucion: {tiempo_out-tiempo_in}')

#-------------------------------------------------------------------------------------------
# Aqui deberia cambiar el metodo overlay por hacerlo manual

def sobreponer_segmentos(segmento1, segmento2):
    return segmento1.overlay(segmento2)


#-------------------------------------------------------------------------------------------
if __name__ == '__main__':
    print("\nMezclador de canciones mp3:\n")
    print("------------------------------")
    print("| Si la ruta esta en la misma carpeta que este programa escribelo asi: './nombre.mp3' |\n")
    archivo1 = input("Introduce la ruta del archivo 1: ")
    archivo2 = input("Introduce la ruta del archivo 2: ")
    out = input("Introduce el nombre del archivo de salida (no incluyas extension): ")
    print("\n------------------------------")
    
    instruccion = input("|Introduce 1 para mezclar en paralelo|\n|Introduce 2 para mezclar en secuencial|\n|Introduce 3 para ambas|\n->")

    if(instruccion == "1"):
        mix_en_paralelo(archivo1, archivo2, out)
    elif(instruccion == "2"):
        mix_en_secuencial(archivo1, archivo2, out)
    elif(instruccion == "3"):
        mix_en_paralelo(archivo1, archivo2, out)
        mix_en_secuencial(archivo1, archivo2, out)
    else:
        print('-1')
    
    print("\n Gracias!\n")
        

"""
Explicacion:

El multiprocessing es un paquete que permite crear procesos usando una API similar al modulo threading
este ofrece una concurrencia tanto local como remote, esquivando el Global Interpreter Lock mediante el 
uso de subprocesos en lugar de hilos(threads).

Pool es un objeto que ofrece un medio de paralelizar la ejecucion de una funcion a traves de multiples
valores de entrada, distribuyendo los datos de entrada a traves de procesos (paralelismo de datos).

Global Interpreter Lock es algo que asegura que el interprete CPython haga que solo un hilo ejecute el 
bytecode Python por vez. Bloqueando el interprete completo se simplifica hacerlo multi-hilos, a costa
de mucho del paralelismo ofrecido por maquinas con multiples procesadores.

"""