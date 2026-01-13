# 🔒 Política de Seguridad

## ⚠️ Reporte de Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, por favor:

1. **NO** crees un issue público
2. Contacta directamente al mantenedor del proyecto
3. Proporciona detalles sobre la vulnerabilidad

## 🛡️ Buenas Prácticas

### Configuración SSH

- **Nunca** subas archivos de configuración con contraseñas al repositorio
- Usa claves SSH en lugar de contraseñas cuando sea posible
- Protege tus archivos de configuración con permisos restrictivos:
  ```bash
  chmod 600 ~/.youtube_downloader/ssh_config.json
  ```

### Datos Sensibles

- Las contraseñas se almacenan en texto plano localmente
- Los archivos de configuración están excluidos del repositorio mediante `.gitignore`
- Nunca compartas tus archivos de configuración

### Verificación

Antes de hacer commit, verifica que:
- ✅ No hay contraseñas hardcodeadas en el código
- ✅ No hay archivos de configuración con datos sensibles
- ✅ El `.gitignore` está actualizado
- ✅ Los archivos de ejemplo no contienen datos reales
