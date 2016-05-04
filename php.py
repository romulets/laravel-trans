class serialize:

	def __init__ (self, dictionary):
		self.__data = []
		for key in list(dictionary):
			self.__data.append(array(key, dictionary[key]))


	def to_file(self, filename):
		file = open(filename, 'w+')
		string = '<?php\n\n'
		string += 'return ' + str(self) + ';'
		file.write(string)
		file.close()

	def __str__(self):
		string = "[\n"

		for row in self.__data:
			string += str(row) + ",\n"


		string += "\n]"
		return string


class array:

	def __init__(self, key, value):
			self.__key = key
			if type(value) is dict:
				self.__value = serialize(value)
			else:
				self.__value = value

	def __str__(self):
		if type(self.__value) is serialize:
			return "'" + self.__key + "' => " + str(self.__value)
		else:
			return "'" + self.__key + "' => '" + str(self.__value).replace("'", "\\'") + "'"


