function popupFun(form_heading){
    const popup = document.createElement('div');
    popup.classList = 'popup h-full w-full fixed top-0 left-0 z-[51] p-6';
    popup.innerHTML = `
        <div class="h-full w-full opacity-75 bg-slate-900 absolute top-0 left-0">
        </div>
        <div class="h-auto w-[500px] p-2 bg-blue-100 video_playback opacity-100 absolute top-2/4 left-2/4 translate-x-[-50%] translate-y-[-50%] overflow-hidden rounded-2xl">
            <div class='mt-4 mb-2 w-full text-slate-900 flex justify-center text-xl'>Upload ${form_heading}</div>
            <div class='error_message capitalize mt-1 mb-3 h-4 w-full text-slate-100 flex justify-center text-md text-red-500 font-bold'></div>
            <div class="w-full p-2 flex flex-col items-center">
              <div class="w-full h-auto p-1">
                <div class="w-full flex">
                  <div class="w-1/4 flex items-center select-none">Title</div>
                  <div class="w-3/4">
                    <input type="text" class="title py-3 px-4 block my-2 w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" placeholder="Title" required>
                  </div>
                </div>
                <div class="w-full h-auto p-1">
                  <div class="w-full flex">
                    <div class="w-1/4 flex items-center select-none">Description</div>
                    <div class="w-3/4">
                      <textarea class="description resize-none py-3 px-4 block my-2 w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" rows="3" placeholder="Description"></textarea>
                  </div>
                </div>

                
                <div class="w-full flex">
                  <div class="w-1/4 flex items-center select-none">Cover Picture</div>
                  <div class="w-3/4">

                    <div class="cover_picture_view w-full flex justify-center items-center flex-col"></div>

                    <input type="file" name="file-input" class="cover_picture block my-2 w-full bg-slate-100 border border-gray-200 shadow-sm rounded-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600 file:bg-gray-50 file:border-0 file:bg-gray-100 file:me-4 file:py-3 file:px-4 dark:file:bg-gray-700 dark:file:text-gray-400">
                  </div>
                </div>

                <div class="w-full flex">
                  <div class="w-1/4 flex items-center select-none">Source</div>
                  <div class="w-3/4">
                    <input type="checkbox" id="yt_video" name="file-input" class="my-2 self-start"><label for="yt_video" class="mx-2 text-slate-700 select-none cursor-pointer">Youtube Link Upload</label>
                  </div>
                </div>

                <div class="w-full flex">
                  <div class="w-1/4 flex items-center select-none">Video File</div>
                  <div class="w-3/4">

                    <div class="video_link_view w-full flex justify-center items-center flex-col"></div>


                    <input type="file" name="file-input" class="video_link file block my-2 w-full bg-slate-100 border border-gray-200 shadow-sm rounded-lg text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600 file:bg-gray-50 file:border-0 file:bg-gray-100 file:me-4 file:py-3 file:px-4 dark:file:bg-gray-700 dark:file:text-gray-400">

                    <input type="text" class="youtube_link title hidden py-3 px-4 block my-2 w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" placeholder="Youtube Link" required>
                  </div>
                </div>

                <button type="button" class="upload_submit py-3 px-4 m-2 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-teal-500 text-white hover:bg-teal-600 disabled:opacity-50 disabled:pointer-events-none dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600">
                    Upload
                  </button>
              </div>
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

    const yt_video = document.getElementById('yt_video');
    const video_link = document.querySelector('.video_link'); 
    const youtube_link = document.querySelector('.youtube_link'); 

    yt_video.addEventListener('click', (e)=>{
      if (e.target.checked){
        video_link.classList.add('hidden')
        youtube_link.classList.remove('hidden')
      } else {
        video_link.classList.remove('hidden')
        youtube_link.classList.add('hidden')
      }
    })

    document.addEventListener('keyup', (e)=>{
      if (e.key == 'Escape'){
        popup_check = false;
        const popup = document.querySelector('.popup');
        popup.remove()
      }
    })

}