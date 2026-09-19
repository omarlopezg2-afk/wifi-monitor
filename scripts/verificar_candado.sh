#!/usr/bin/env bash
# verificar_candado.sh — comprueba que el candado viaja DENTRO de los paquetes.
#
# POR QUÉ EXISTE
# Si el bundle sale sin licensing.py la app NO falla: el import cae en el except
# de wifi_monitor.py, is_premium() devuelve True y la app abre completa y en
# silencio (fail-open deliberado). Este script es lo que impide publicar una
# versión sin candado: compara el licensing.py empaquetado, byte a byte, con el
# del repo. Sin esta comprobación, el único síntoma sería no cobrar.
#
# USO
#   bash scripts/verificar_candado.sh WiFiMonitor_*.deb WiFiMonitor-*.AppImage
#
# Sale 0 si todos los paquetes lo llevan, 1 si alguno no (y GitHub marca el
# step en rojo). Los paquetes que no existan se avisan y se omiten.

set -u

if [ ! -f licensing.py ]; then
  echo "::error::no encuentro licensing.py: ejecuta este script desde la raíz del repo"
  exit 1
fi

esperado=$(sha256sum licensing.py | awk '{print $1}')
fallo=0

for paquete in "$@"; do
  if [ ! -e "$paquete" ]; then
    echo "::warning::no existe $paquete, se omite"
    continue
  fi

  caso=$(mktemp -d)
  abs=$(readlink -f "$paquete")

  case "$paquete" in
    *.deb)
      if ! dpkg-deb -x "$abs" "$caso"; then
        echo "::error::no se pudo extraer $paquete"
        fallo=1
        rm -rf "$caso"
        continue
      fi
      ;;
    *.AppImage)
      chmod +x "$abs"
      # --appimage-extract no necesita FUSE: descomprime en ./squashfs-root
      (cd "$caso" && "$abs" --appimage-extract >/dev/null 2>&1) || true
      ;;
    *)
      echo "::warning::tipo de paquete no reconocido: $paquete"
      rm -rf "$caso"
      continue
      ;;
  esac

  encontrado=$(find "$caso" -name licensing.py -print -quit 2>/dev/null)

  if [ -z "$encontrado" ]; then
    echo "::error::$paquete NO contiene licensing.py — el candado no viaja y la app abriría completa en silencio"
    fallo=1
  else
    real=$(sha256sum "$encontrado" | awk '{print $1}')
    if [ "$real" != "$esperado" ]; then
      echo "::error::$paquete trae un licensing.py DISTINTO al del repo ($real != $esperado)"
      fallo=1
    else
      echo "OK  $paquete — licensing.py presente e idéntico al repo ($(stat -c '%s' "$encontrado") bytes)"
    fi
  fi

  rm -rf "$caso"
done

if [ "$fallo" -eq 0 ]; then
  echo "Candado verificado en todos los paquetes."
fi
exit "$fallo"
