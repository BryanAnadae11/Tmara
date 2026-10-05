module.exports = {
  apps: [
    {
      name: "Tmara",
      cwd: "/var/www/apps/Tmara",
      script: "/var/www/apps/Tmara/venv/bin/gunicorn",
      args: "--bind 127.0.0.1:8001 Tmaraproj.wsgi:application",
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_memory_restart: "400M",
      env: {
        PYTHONUNBUFFERED: "1",
        DJANGO_SETTINGS_MODULE: "Tmaraproj.settings"
      }
    }
  ]
};
