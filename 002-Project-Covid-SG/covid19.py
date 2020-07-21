from covid import Covid

def info_covid(country):
    covid = Covid()
    return covid.get_status_by_country_name(country)

print(info_covid('Turkey'))
