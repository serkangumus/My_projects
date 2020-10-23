from flask import Flask, render_template, request

app = Flask(__name__)

def convert_to_roman(num):
	roman = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
	sayi = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
	romanvalue = ""
	for i, d in enumerate(sayi):
		while (num >= d):
			num -= d
			romanvalue += roman[i]
	return romanvalue

@app.route('/', methods = ['GET'])
def main_get():
    return render_template('index.html', developer_name = 'Serkan', not_valid = False)

@app.route('/', methods = ['POST'])
def main_post():
    alpha = request.form['number']
    if not alpha.isdecimal():
        return render_template('index.html', developer_name = 'Serkan', belkis = True)
    number = int(alpha)
    if not 0 < number < 4000:
        return render_template('index.html', developer_name = 'Serkan',  belkis = True)
    return render_template('result.html', number_decimal = number, number_roman = convert_to_roman(number), developer_name = 'Serkan')

if __name__=='__main__':
    #app.run()
    #app.run(debug=True)
    app.run('0.0.0.0',port=80)





