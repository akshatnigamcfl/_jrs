function addLoader(){
    const dv = document.createElement('div');
    dv.setAttribute('class', 'main_loader absolute w-screen h-screen bg-[rgba(0,0,0,0.9)] opacity-50 z-50 flex justify-center items-center')
    dv.innerHTML = `<span class="loading loading-dots loading-lg text-white"></span>`;
    document.body.prepend(dv)
}

function removeLoader(){
    const main_loader = document.querySelector('.main_loader');
    main_loader.remove()
}