class UtilsDescriptions:

    def check_proportions(self, list_values):
        counts_y = list_values.value_counts().to_list()
        return round(counts_y[0]/counts_y[1])

    def represent_to_proportions(self, train, test):
        train_proportion = self.check_proportions(train)
        test_proportion = self.check_proportions(test)
        print(f"A proporcão do treino é de {train_proportion}/1")
        print (f"Equnadom  a proporção do teste é de {test_proportion}/1")