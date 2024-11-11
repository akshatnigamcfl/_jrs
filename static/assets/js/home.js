const shopByColor_navLinks = document.querySelector('div.nav_links ul li.shop_by_color');
const cancel_dropdown = document.querySelector('div.cancel_dropdown i.fa-solid.fa-xmark')

let isdrop = false;
shopByColor_navLinks.addEventListener('click', ()=>{
    let dropbox = document.querySelector('.dropdown_menu');
let dropdown_tilt = document.querySelector('li.shop_by_color i.fa-solid.fa-caret-down');

if(isdrop){
    dropbox.classList.remove('dropdown_visible');
    console.log('True');
    dropdown_tilt.classList.remove('drop_tilt');
} else {
    dropbox.classList.add('dropdown_visible');
    console.log('False');
    dropdown_tilt.classList.add('drop_tilt');
}
    isdrop = !isdrop;
})


// function scroll_amount(){
// let header = document.querySelector('div.lower_header--block');
// let page_cordinate = window.pageYOffset;
//     // if(page_cordinate > 42){
//     //     header.classList.add('sticky-header');
//     // } else {
//     //     header.classList.remove('sticky-header');
//     // }

// let header_color = document.querySelector('div.lower_header--block');

// if(page_cordinate > 603){
//     header_color.style.background = 'rgba(0,0,0,0.67)';
//     console.log('greater')
// } else {
//     header_color.style.background = 'transparent';
//     console.log('else condition') 
// }

// }

// document.addEventListener('scroll', scroll_amount);


let portF = document.querySelector('section.view_portfolio div.up_content');
document.addEventListener('scroll', ()=>{
let page_cordinate = window.pageYOffset;
if(page_cordinate > 8637){
    portF.classList.add('scroll_tup');
    console.log('added');
} else {
    portF.classList.remove('scroll_tup');
}
})