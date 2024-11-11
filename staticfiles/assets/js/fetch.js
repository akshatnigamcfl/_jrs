async function ftN(link, method, headers, body){
    // console.log('link', link)
    let a
    if (body !== ''){
        a = await fetch(link, {'method': method, headers: headers, body: body})
    } else{
        a = await fetch(link, {'method': method, headers: headers})
    }
    a = await a.json()
    return a
}