function getCookies() {
    const cookies = document.cookie.split(';');
    const cookieObject = {};
    cookies.forEach(cookie => {
        const [key, value] = cookie.split('=').map(c => c.trim());
        cookieObject[key] = decodeURIComponent(value);
    });
    console.log('cookies', cookieObject)
    return cookieObject;
}

function edF(val){
    var str = ''
    for (var i=0; i<val.length; ){
        if (val[i] === '.') {
            str += val.substring(i, i+3) + ','
            i+=3

        } else {
            str += val.substring(i, i+1 ) + ','
            i++
        }
    } 
    return str;
}

function ed(value) {
    // console.log('asdf', value.split("").map(e=>e.charCodeAt()).map((e,i,a)=>edF(getCookies().ed)))
    return value.split("").map(e=>e.charCodeAt()).map((e,i,a)=>edF(getCookies().ed).split(',')[e-32]).join("");
}