async function memberPopupFun(form_heading){
  const popup = document.createElement('div');
  popup.classList = 'popup h-full w-full fixed top-0 left-0 z-[51] p-6';


  popup.innerHTML = `
    <div class="h-full w-full opacity-75 bg-slate-900 absolute top-0 left-0">
    </div>
    <div class="h-auto w-96 bg-white video_playback opacity-100 absolute top-2/4 left-2/4 translate-x-[-50%] translate-y-[-50%] overflow-hidden rounded-2xl">
      <div class='h-[40px] relative w-full bg-slate-800 text-white flex justify-center items-center text-base'>
        <span class="select-none">${form_heading}</span>
        <div class="close_btn_dv h-7 w-7 absolute top-[50%] translate-y-[-50%] right-[3%] rounded-full flex justify-center items-center bg-red-700">
          <img class="w-5 h-5 hover:h-6 hover:w-6 duration-300" src="/static/assets/images/icons/close_button.png">
        </div>
      </div>
      <div class='error_message capitalize mt-2 h-4 w-full text-slate-100 flex justify-center text-xs text-red-500 font-bold'></div>
        <div class="w-full p-2   flex flex-col items-center">


          <div class="w-full h-auto p-1">
            <div class="w-full flex">
              <div class="w-1/4 flex items-center select-none text-xs">Name</div>
              <div class="w-3/4">
                <input type="text" class="title border text-xs py-3 px-4 block my-1 w-full border-gray-200 rounded-lg focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" required>
              </div>
            </div>
          </div>

          <div class="w-full h-auto p-1">
            <div class="w-full flex">
              <div class="w-1/4 flex items-center select-none text-xs">Contact Number</div>
              <div class="w-3/4">
                <input type="number" class="contact_number border text-xs py-3 px-4 block my-1 w-full border-gray-200 rounded-lg focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" required>
            </div>
          </div>

          <div class="w-full h-auto p-1">
            <div class="w-full flex">
              <div class="w-1/4 flex items-center select-none text-xs">Email</div>
              <div class="w-3/4">
                <input type="email" class="email_id border text-xs py-3 px-4 block my-1 w-full border-gray-200 rounded-lg focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" required>
            </div>
          </div>



          <div class="w-full h-auto p-1">
            <div class="w-full flex">
              <div class="w-1/4 flex items-center select-none text-xs">Shoot Category</div>
              <div class="w-3/4">
                <div class="skills_cont border rounded-lg w-full h-auto flex flex-col p-3 text-xs"></div>
            </div>
          </div>

          <div class="trash_cont w-3/4 my-2 flex justify-center my-2 select-none"></div>


          <div class="flex justify-center mt-4">
            <button type="button" class="submit py-2 px-4 inline-flex items-center gap-x-2 text-xs font-semibold rounded-lg border border-transparent bg-teal-500 text-white hover:bg-teal-600 disabled:opacity-50 disabled:pointer-events-none dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600">Submit</button>
          </div>

        </div>
    </div>

  `



  // popup.innerHTML = `
  //     <div class="h-full w-full opacity-75 bg-slate-900 absolute top-0 left-0"></div>
  //     <div class="h-[500px] w-96 pt-0 video_playback opacity-100 absolute top-2/4 left-2/4 translate-x-[-50%] translate-y-[-50%] overflow-hidden rounded-2xl">
  //       <div class='h-[50px] relative w-full bg-slate-800 text-white flex justify-center items-center text-lg'>
  //         <span class="select-none">${form_heading}</span>
  //         <div class="close_btn_dv h-7 w-7 absolute top-[50%] translate-y-[-50%] right-[3%] rounded-full flex justify-center items-center bg-red-700">
  //           <img class="w-5 h-5 hover:h-6 hover:w-6 duration-300" src="/static/assets/images/icons/close_button.png">
  //         </div>
  //       </div>
        
  //       <div class="bg-white h-[calc(100%-110px)] overflow-y-scroll">
  //         <div class='error_message capitalize p-4 mb-3 h-4 w-full text-slate-100 flex justify-center text-sm text-red-500 font-medium'></div>
  //         <div class="w-full p-2 flex flex-col items-center justify-center">
  //                 <div class="w-3/4 my-2">
  //                 <span class="text-md select-none">Name</span>
  //                   <input type="text" class="title border text-sm py-3 px-4 block my-1 w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" required>
  //                 </div>

  //               <div class="w-3/4 my-2">
  //                 <span class="text-md select-none">Contact Number</span>
  //                 <input type="number" class="contact_number border text-sm py-3 px-4 block my-1 w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" required>
  //               </div>

  //               <div class="w-3/4 my-2">
  //               <span class="text-md select-none">Email</span>
  //                 <input type="email" class="email_id border text-sm py-3 px-4 block my-1 w-full border-gray-200 rounded-lg text-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:pointer-events-none dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400 dark:focus:ring-gray-600" required>
  //               </div>

  //               <div class="w-3/4 my-2">
  //               <span class="text-md select-none">Shoot Category</span>
  //                 <div class="skills_cont border rounded-lg w-full h-auto flex flex-col p-3">
  //                 </div>
  //               </div>


  //           <div class="trash_cont w-3/4 my-2 flex justify-center my-2 select-none"></div>
  //         </div>
  //       </div>

  //       <div class="flex bg-white justify-center h-[60px] w-full">
  //         <button type="button" class="submit py-3 h-10 w-3/4 text-center px-4 m-2 inline-flex justify-center items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-teal-500 text-white hover:bg-teal-600 disabled:opacity-50 disabled:pointer-events-none dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600">Submit</button>
  //       </div>
  //     </div>
  //   `


    // <div class="w-[40%] flex items-center select-none text-sm">Email Id</div>



    function getCookies() {
      const cookies = document.cookie.split(';');
      console.log('cookies', cookies)
      const cookieObject = {};
      cookies.forEach(cookie => {
          const [key, value] = cookie.split('=').map(c => c.trim());
          cookieObject[key] = decodeURIComponent(value);
      });
      return cookieObject;
  }



  let token = getCookies().access
  let a = await fetch('/api/get_skills', {method:'GET', headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`} })
  console.log('a',a)
  a = await a.json()
  if (a) {
    const skills_cont = popup.querySelector('.skills_cont')
    if (a.status === 200){
      a.data.forEach(e=>{
        const div = document.createElement('div');
        div.classList.value = 'w-full h-6'
        div.innerHTML=`<label class="cursor-pointer skills_item"><input class="skills" type="checkbox" data-service-id=${e.id}><span class="ml-2 capitalize select-none">${e.service_name}<span></label>`
        skills_cont.append(div)
      })
    } else{
      console.log('something went wrong')
    }
  }



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

  return true

}
