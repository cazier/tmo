/* global localStorage */

class DarkMode {
  buttonSelector = '#dark_toggle'

  constructor () {
    const state = localStorage.getItem('dark_mode')
    if (state === null) {
      this.on = window.matchMedia('(prefers-color-scheme: dark)').matches
    } else {
      this.on = JSON.parse(state)
    }
  }

  get enabled () {
    return this.on
  }

  set enabled (state) {
    this.on = state
    document.documentElement.dataset.theme = state ? 'dark' : ''
    localStorage.setItem('dark_mode', JSON.stringify(state))
  }

  set () {
    this.enabled = this.enabled // eslint-disable-line no-self-assign
  }

  setIcon () {
    const icon = document.querySelector(this.buttonSelector + ' i')

    if (this.enabled) {
      icon.classList.remove('fa-moon')
      icon.classList.add('fa-sun')
    } else {
      icon.classList.remove('fa-sun')
      icon.classList.add('fa-moon')
    };
  }

  click () {
    this.enabled = !this.enabled
    this.setIcon()
  }
}

const dm = new DarkMode()

window.addEventListener('load', () => {
  dm.setIcon()

  document.querySelector(dm.buttonSelector).addEventListener('click', () => {
    dm.click()
  })
})
