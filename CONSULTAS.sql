SELECT * FROM plataformas where cond_pla=1

insert into plataformas (nom_pla,cond_pla) values ('Netflix',1)

select * from ventas

select * from cuentas
insert into cuentas (cod_pla,cod_ven,correo,password,perfil,clave,tiempo,fec_ini,fec_cul,cond_cue) values (1,1,'dany2000sr@gmail.com','fredy200','Fredy','1616',30,'2025-07-5','2025-08-4',1)

SELECT plataformas.nom_pla,cuentas.cod_ven,cuentas.correo,cuentas.password,cuentas.perfil,cuentas.clave,cuentas.tiempo,cuentas.fec_ini,cuentas.fec_cul,cuentas.cond_cue FROM cuentas,plataformas where cond_cue=1

SELECT 
    cuentas.cod_cue,
    plataformas.nom_pla,
    cuentas.cod_ven,
    cuentas.correo,
    cuentas.password,
    cuentas.perfil,
    cuentas.clave,
    cuentas.tiempo,
    cuentas.fec_ini,
    cuentas.fec_cul,
    cuentas.cond_cue,
    ROUND(julianday(cuentas.fec_cul) - julianday('now')) AS dias_restantes
FROM 
    cuentas, plataformas
WHERE 
    cond_cue = 1
ORDER BY 
    cod_cue;

	
SELECT * FROM estadocuentas

INSERT INTO estadocuentas (nom_est, cond_est) VALUES ('Activo',1)

select * from tiponotificacion
insert into tiponotificacion (nom_tip,tiempo,cond_tip_not) values ('Próximo a vencer','3 días antes de vencer',1)


select * from notificaciones
INSERT INTO notificaciones (fec_not, cod_cue, tip_not, cond_not) VALUES ('2025-07-06',2,1,1)

SELECT notificaciones.fec_not,cod_cue, tiponotificacion.nom_tip FROM notificaciones,tiponotificacion WHERE notificaciones.cond_not=1


SELECT * FROM tiponotificacion WHERE cond_tip_not = 1


select * from plataformas


DELETE FROM plataformas;
DELETE FROM sqlite_sequence WHERE name='plataformas';


SELECT cuentas.cod_cue,plataformas.nom_pla,
cuentas.cod_ven,cuentas.correo,cuentas.password,
cuentas.perfil,cuentas.clave,cuentas.tiempo,cuentas.fec_ini,cuentas.fec_cul,cuentas.cond_cue, 
ROUND(julianday(cuentas.fec_cul) - julianday(date('now'))) AS dias_restantes
FROM cuentas,plataformas 
where cond_cue=1 AND plataformas.cod_pla=cuentas.cod_pla ORDER BY cod_cue