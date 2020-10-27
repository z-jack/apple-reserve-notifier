# apple-reserve-notifier

A tool to automatically fetch the stock and push notification using WebHook

## Usage

- First, Copy `config.example.json` to `config.json`
- Set the `config.json` to your desired parameters
- run `python3 refreshProducts.py` to load products informations
- run `python3 notifier.py` to automatically fetch the reserve status

## Config Format

Here is an example `config.json`.

```JavaScript
{
	"webHookUrl": "CLI", // When Using "CLI" mode, the notification will output to console. Otherwise, will make a post request to your set URL
	"contentType": "text/plain", // the MIME type of post data
	"webHookFormat": "✨ The product {{ productName }} is now available in {{ storeName }}, {{ city }}. Go to {{ reserveUrl }} to reserve it now!", // The message needed to show, can also be other JSON content
	// There are some template that will be replaced to real data, use {{}} to told program this is a template
	// =====
	// productName: the name of this product in your setting language
	// productSeries: the unique id of product
	// productColor: the color of this product
	// productCapacity: the capacity of this product
	// productPrice: the price of this product (currency unit is depending on your country setting)
	// city: the city of selling store
	// storeNumber: the unique id of store
	// storeName: the name of store
	// reserveUrl: the URL of reservation
	// =====
	"country": "CN", // Buyer's country
	"language": "zh_CN", // Your perferred language
	"filterCities": ["上海"], // Which city(ies) you are looking for, leave empty if you want all cities
	"filterStores": ["R705", "上海环贸 iapm"], // Which store(s) you are looking for, use storeNumber or storeName, leave empty if you want all stores
	"queryInterval": 10 // the interval of each stock query (in seconds)
}
```
