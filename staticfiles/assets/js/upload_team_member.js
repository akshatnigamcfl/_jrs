function memberPopupFun(form_heading){
  const popup = document.createElement('div');
  popup.classList = 'popup h-full w-full fixed top-0 left-0 z-[51] p-6';
  popup.innerHTML = `
      <div class="h-full w-full opacity-75 bg-slate-900 absolute top-0 left-0">
      </div>
      <div class="h-auto w-[500px] p-2 bg-blue-100 video_playback opacity-100 absolute top-2/4 left-2/4 translate-x-[-50%] translate-y-[-50%] overflow-hidden rounded-2xl">
        <div class='mt-4 mb-2 w-full text-slate-900 flex justify-center text-xl'>${form_heading}</div>
        <div class='error_message capitalize mt-1 mb-3 h-4 w-full text-slate-100 flex justify-center text-md text-red-500 font-bold'></div>
        <div class="w-full p-2 flex flex-col items-center">
            
            <div class="w-full h-auto p-1">
                <div class="w-full flex">
                  <div class="w-[40%] flex items-center select-none text-sm">Name</div>
                  <div class="w-3/4">
                    <input type="text" class="title text-sm py-3 px-4 block my-2 w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" placeholder="Name" required>
                  </div>
                </div>
            </div>

            <div class="w-full h-auto p-1">
              <div class="w-full flex">
                <div class="w-[40%] flex items-center select-none text-sm">Contact Number</div>
                <div class="w-3/4">
                  <input type="number" class="contact_number text-sm py-3 px-4 block my-2 w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" placeholder="Contact Number" required>
              </div>
            </div>

            <div class="w-full h-auto p-1">
              <div class="w-full flex">
                <div class="w-[40%] flex items-center select-none text-sm">Email Id</div>
                <div class="w-3/4">
                  <input type="email" class="email_id text-sm py-3 px-4 block my-2 w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" placeholder="Email Id" required>
                </div>
              </div>
            </div>

            <div class="trash_cont flex p-1"></div>


            <button type="button" class="submit py-3 px-4 m-2 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-teal-500 text-white hover:bg-teal-600 disabled:opacity-50 disabled:pointer-events-none dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600">Submit</button>
        </div>
      </div>

    <div class="close_btn_dv h-8 w-8 absolute top-[2%] right-[3%] rounded-full flex justify-center items-center">
      <img class="w-[90%] h-[90%] hover:h-full hover:w-full duration-300" src="/static/assets/images/icons/close_button_black.png">
    </div>
    `
  document.body.prepend(popup)
  const close_btn = document.querySelector('.close_btn_dv')
  close_btn.addEventListener('click', ()=>{
      const popup = document.querySelector('.popup')
      popup.remove()
  })


  document.addEventListener('keyup', (e)=>{
    if (e.key == 'Escape'){
      popup_check = false;
      const popup = document.querySelector('.popup');
      popup.remove()
    }
  })
}