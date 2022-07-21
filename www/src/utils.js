let base_url = "http://127.0.0.1:5000/"
export function postJSON(url, data){
	return fetch(base_url+url, {
  		method: "POST",
  		headers: {
    		'Content-Type': 'application/json',
  		},
  		body: JSON.stringify(data)
  	}).then(resp => resp.json())
}