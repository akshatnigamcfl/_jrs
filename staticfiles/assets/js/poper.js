function poperFunction(status, message, reload){

  console.log('poper working')

    if (status == 200){
        const dv = document.createElement('div');
        dv.classList = 'submit_alert w-80 absolute left-[50%] translate-x-[-50%] top-4 overflow-hidden shadow-2xl z-[50000000]'
        dv.innerHTML= `<div class="poper_message bg-teal-50 border-t-2 border-teal-500 rounded-lg p-4 dark:bg-teal-800/30" role="alert">
        <div class="flex">
          <div class="flex-shrink-0">
          <span class="inline-flex justify-center items-center w-8 h-8 rounded-full border-4 border-teal-100 bg-teal-200 text-teal-800 dark:border-teal-900 dark:bg-teal-800 dark:text-teal-400">
          <svg class="flex-shrink-0 w-4 h-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="m9 12 2 2 4-4"/></svg>
            </span>
            </div>
          <div class="ms-3">
            <h3 class="text-gray-800 font-semibold dark:text-white capitalize">
            ${message}
            </h3>
            </div>
        </div>
        <div class="submit_alert_duration bg-green-800 w-[100%] h-[6px] absolute bottom-0 left-0 rounded-b-md"></div>
        </div>
        `
        document.body.prepend(dv)
        
        // const submit_alert = document.querySelector('.submit_alert');
        // const submit_alert_duration = submit_alert.querySelector('.submit_alert_duration')
        if (reload===true){
            setTimeout(()=>{
                window.location.reload()
            },2000)
        }


    } else {

  console.log('poper working')

    const dv = document.createElement('div');
    dv.classList = 'submit_alert w-80 absolute left-[50%] translate-x-[-50%] top-4 overflow-hidden shadow-2xl z-[50000000]'
    dv.innerHTML= `<div class="poper_message bg-red-50 border-s-4 border-red-500 p-4 dark:bg-red-800/30 " role="alert">
      <div class="flex">
        <div class="flex-shrink-0">
          <!-- Icon -->
          <span class="inline-flex justify-center items-center w-8 h-8 rounded-full border-4 border-red-100 bg-red-200 text-red-800 dark:border-red-900 dark:bg-red-800 dark:text-red-400">
            <svg class="flex-shrink-0 w-4 h-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </span>
          <!-- End Icon -->
        </div>
        <div class="ms-3">
        <h3 class="text-gray-800 font-semibold dark:text-white">
        Error!
        </h3>
        <p class="text-sm text-gray-700 dark:text-gray-400 capitalize">
        ${message}
        </p>
        </div>
        </div>
        </div>
        </div>
        `
        document.body.prepend(dv)
    }

    const poper_message = document.querySelector('.poper_message');
    setTimeout(()=>{
        poper_message.remove()
    }, 3000)

}