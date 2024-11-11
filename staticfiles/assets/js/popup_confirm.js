function popupConfirmFun(id,message,description, link){
    const popup = document.createElement('div');
    popup.classList = 'popup h-full w-full fixed top-0 left-0 z-[51] p-6';
    popup.innerHTML = `
        <div class="h-full w-full opacity-75 bg-slate-900 absolute top-0 left-0">
        </div>
        <div class="absolute left-[50%] top-[50%] translate-y-[-50%] translate-x-[-50%] card w-96 bg-neutral text-neutral-content">
          <div class="card-body items-center text-center">
            <h2 class="card-title">${message}</h2>
            <p>${description}</p>
            <span class="img_preview"></span>
            <div class="card-actions justify-end">
              <button data-id="${id}" class="confirm btn btn-primary">Accept</button>
              <button class="cancle btn btn-ghost">Deny</button>
            </div>
          </div>
        </div>

        <div class="close_btn_dv h-8 w-8 absolute top-[2%] right-[3%] rounded-full flex justify-center items-center">
            <img class="w-[90%] h-[90%] hover:h-full hover:w-full duration-300" src="/static/assets/images/icons/close_button.png">
        </div>
        `
    document.body.prepend(popup)

    if (link !== null){
      const img_preview = document.querySelector('.img_preview');
      img_preview.innerHTML = `<img class="h-24 w-36 py-3" src = "${link}"></img>`;
    }


    const close_btn = document.querySelector('.close_btn_dv')
    const cancle = document.querySelector('.cancle')
    // const popup = document.querySelector('.popup')

    cancle.addEventListener('click', ()=>{
        popup.remove()    
    })
    close_btn.addEventListener('click', ()=>{
        popup.remove()
    })
}