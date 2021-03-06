from gestureRecognitionClass import GestureRecognition
import pandas


class ReadSerialData:

    def __init__(self):
        self.gestureNum = 0

        # Creating an instance of the gesture recognition class
        self.GR = GestureRecognition()

        while 1 == 1:
            print('\n\n\t   Gesture Detection Control Panel\n')
            print('\t 1. Press " r " to RECORD SAMPLE')
            print('\t 2. Press " v " to VIEW TRAINING (GESTURES RECORDED)')
            print('\t 3. Press " t " to TRAIN THE DEVICE')
            print('\t 4. Press " p " to START PREDICTION\n')
            print('\t Press Ctrl+C to Stop current action.\n')

            choice = input('Enter your choice : ')

            if choice == 'e':
                break

            elif choice == 'r' or choice == 'R':
                self.GR.recordGesture()

            elif choice == 'v' or choice == 'V':
                readData = pandas.read_csv('TrainingData.csv')
                sample = readData.set_index('gest_num')
                print("\n")
                print(type(sample))
                print(sample)

            elif choice == 'T' or choice == 't':
                print("\n\tStarting device training....")
                self.GR.train()
                print("\n\tDevice training Successful.")

            elif choice == 'P' or choice == 'p':
                print("\n\t\tPredicting gestures.....")
                val = self.GR.startPredicting()
                for i in val:
                    print(i)

ReadSerialData()
